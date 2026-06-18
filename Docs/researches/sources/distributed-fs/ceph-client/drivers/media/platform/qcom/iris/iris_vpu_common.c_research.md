# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vpu_common.c

## Purpose
`iris_vpu_common.c` implements shared Iris VPU controller and hardware power, firmware boot, interrupt, watchdog, power-collapse, and clock-frequency helper logic. It is the common hardware-control layer behind per-platform `vpu_ops`, abstracting register programming differences while coordinating clocks, power domains, interconnect bandwidth, IRQ state, and firmware boot memory maps.

## Important APIs And Functions
- Boot and interrupt control: `iris_vpu_boot_firmware()`, `iris_vpu_raise_interrupt()`, `iris_vpu_clear_interrupt()`, `iris_vpu_watchdog()`.
- Power collapse and power sequencing: `iris_vpu_prepare_pc()`, `iris_vpu_power_on_controller()`, `iris_vpu_power_on_hw()`, `iris_vpu_power_on()`, `iris_vpu_power_off_controller()`, `iris_vpu_power_off_hw()`, `iris_vpu_power_off()`, `iris_vpu_set_hwmode()`, `iris_vpu_switch_to_hwmode()`.
- VPU35/VPU4x-specific controller operations: `iris_vpu35_vpu4x_power_on_controller()`, `iris_vpu35_vpu4x_power_off_controller()`, `iris_vpu35_vpu4x_program_bootup_registers()`.
- Performance model: `iris_vpu3x_vpu4x_calculate_frequency()` computes required VPU frequency from frame size, FPS, firmware cycles, VPP/VSP cycles, pipe count, and stage.
- Internal helpers include `iris_vpu_interrupt_init()` and `iris_vpu_setup_ucregion_memory_map()`.

## Control Flow
Firmware boot first programs the UC region and queue table addresses in `iris_vpu_setup_ucregion_memory_map()`, including 4 KiB queue-table alignment and 1 MiB UC region size alignment, then writes `CTRL_INIT` and polls `CTRL_STATUS` until firmware reports boot progress or an invalid UC-region setting. On success it enables host-to-Xtensa interrupts and clears X2RPMH state.

Power-on flows vote maximum interconnect bandwidth, enable controller power and clocks through platform ops, enable hardware power/clocks, set OPP frequency, apply preset registers, unmask VPU interrupts, clear `core->intr_status`, and enable IRQ delivery. Error unwinding disables controller resources and interconnect votes in reverse order.

Power-off clears OPP rate, powers off hardware then controller through platform ops, drops interconnect votes, and disables IRQ when the last interrupt status was not a watchdog. Controller power-off sequences write X2RPMH and NOC low-power requests, poll LPI status registers, halt/debug bridge clocks, toggle resets, and then disable clocks/power domains. VPU35/VPU4x uses a retry loop for AON video-control NOC LPI handshake and resets controller clocks after power down.

Power-collapse preparation checks `CTRL_STATUS` PC-ready and idle bits plus TZ CPU WFI status, asks firmware via `sys_pc_prep`, then polls for PC-ready and WFI status. If any condition fails it logs current state and returns `-EAGAIN`.

## State And Persistence
- Mutates hardware registers through `core->reg_base` and offsets from `iris_vpu_register_defines.h`.
- Uses `core->iface_q_table_daddr`, `core->sfr_daddr`, `core->intr_status`, `core->irq`, `core->power.clk_freq`, and platform data including power domains, clocks, resets, core architecture, and `vpu_ops`.
- No persistent storage is written; state lives in device registers, runtime PM resources, and `iris_core`.

## Dependencies And Integration Points
- Linux APIs: `readl/writel`, `readl_poll_timeout`, reset bulk reset, PM domains, OPP, IRQ, sleeps.
- Iris subsystems: `iris_core`, instance state, HFI queue table definitions, clock/power-domain helpers, interconnect helpers, and platform data callbacks.
- Integrates with HFI through `core->hfi_ops->sys_pc_prep()` and interrupt signaling registers.

## Risks And Edge Cases
- Firmware boot timeout is fixed at 1000 polls with 50-100 us sleeps; slow firmware or bad register programming yields `-ETIME`.
- Power-off controller functions often continue to disable resources after LPI poll failures and return `0`, so failures are logged or implied rather than propagated.
- `core->sfr_daddr + core_arch` is written to SFR address; incorrect architecture offset or DMA address truncation to `u32` can break firmware debug/boot on address layouts beyond the expected mask.
- IRQ disable is skipped on watchdog status, which is intentional for fault handling but must be considered in recovery races.
- Frequency calculation assumes default FPS and valid firmware caps; pipe count of zero would be invalid for `mult_frac` divisor.

## Test Signals
- Probe/boot should complete with firmware queues initialized and interrupts unmasked.
- Suspend/resume and idle power-collapse should show successful `sys_pc_prep` and no "skip power collapse" logs under idle workloads.
- Watchdog/fault tests should trigger `-ETIME` and preserve recovery path behavior.
- Clock/power-domain traces should show balanced enable/disable on probe failure, runtime suspend, stream start, and stream stop.
