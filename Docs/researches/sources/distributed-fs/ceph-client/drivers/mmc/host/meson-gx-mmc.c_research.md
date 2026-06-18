# sources/distributed-fs/ceph-client/drivers/mmc/host/meson-gx-mmc.c

## Purpose

`meson-gx-mmc.c` implements the Amlogic GX/GXBB/GXL/GXM/AXG SD/eMMC host controller driver. It manages the controller clock tree, descriptor-chain DMA or bounce-buffer transfers, SDIO IRQs, tuning/resampling, voltage switching, and a G12A-style DRAM access quirk that uses the controller's internal SRAM instead of DDR.

## Important APIs, Types, And Functions

- Register macros define clock, delay/adjust, descriptor start, config, status, IRQ, command descriptor, response, and SRAM data-buffer registers.
- `struct meson_mmc_data` captures SoC-specific clock delay masks, always-on bit, adjust register offset, and SDIO sleep bit.
- `struct sd_emmc_desc` is the four-word hardware command/data descriptor.
- `struct meson_host` stores device/MMC pointers, clock handles, current command, request clock and DDR state, DRAM quirk flag, pinctrl clock-gate state, bounce and descriptor DMA buffers, IRQ, pre/post tracking, and SDIO IRQ lock.
- `meson_mmc_clk_init()` creates a controller-local mux and divider clock from `clkin0`/`clkin1`, initializes register defaults, and enables the MMC clock.
- `meson_mmc_clk_set()` gates/ungates the clock safely, programs DDR mode, sets the clock rate, and updates `mmc->actual_clock`.
- `meson_mmc_pre_req()`/`post_req()` choose descriptor-chain mode based on alignment and block constraints and map/unmap SGs.
- `meson_mmc_start_cmd()` builds direct command registers or descriptor-chain entries, handles bounce-buffer copies, and kicks command execution.
- `meson_mmc_irq()` acknowledges SDIO, CRC, timeout, and end-of-chain/status interrupts and wakes the thread for completion.
- `meson_mmc_irq_thread()` copies bounce reads back, follows SBC/main/stop sequencing through `meson_mmc_get_next_command()`, and completes requests.
- `meson_mmc_resampling_tuning()` sweeps resampling delay values with `mmc_send_tuning()`.

## Control Flow And State

Requests enter `meson_mmc_request()`, which checks DRAM-quirk alignment, decides whether pre/post mapping is needed, stops any current descriptor execution, and starts either SBC or the main command. `meson_mmc_start_cmd()` stores `host->cmd`, programs response/data flags, chooses descriptor-chain or bounce-buffer mode, copies write data when needed, writes descriptors/registers with memory barriers, and starts hardware.

Interrupt handling is split: the hard IRQ acks status, handles SDIO IRQs under a spinlock, sets command errors for CRC/timeouts, reads responses, marks bytes transferred on successful data completion, stops descriptors on errors, and wakes the threaded handler. The thread waits for descriptor stop on errors or copies read bounce data on success, then either starts the next command in the request (main after CMD23, stop after multi-block) or calls `meson_mmc_request_done()`.

Clock state persists in `host->req_rate`, `host->ddr`, and `mmc->actual_clock`. Resampling state is held in the adjust register and reset/disabled for legacy and high-speed non-tuned modes. SDIO IRQ enable state is the IRQ_EN register guarded by `host->lock`.

## Dependencies And Integration Points

The driver integrates with platform resources, OF match data, MMC core, GPIO card-detect IRQs, regulators, reset controller, pinctrl clock-gate state, Linux clock framework, DMA coherent allocation/mapping, threaded IRQs, and SDIO IRQ work. Compatible data selects GX v2 or AXG v3 clock delay layouts.

## Risks And Edge Cases

- Descriptor-chain mode is only safe for aligned SG offsets and block-aligned lengths for multi-block/SDIO CMD53 transfers. The driver falls back to bounce mode and warns once when constraints are not met.
- The DRAM access quirk requires 32-bit aligned SG offsets and lengths and limits transfer size to the internal SRAM buffer.
- Clock gating is hardware-sensitive; if the `clk-gate` pinctrl state is absent, the driver uses the controller stop-clock bit, which comments describe as less safe.
- Error paths stop descriptor execution and wait for idle to prevent late IRQs after request completion.
- HS400 is explicitly disabled because reliable support is unclear.
- `host->needs_pre_post_req` handles requests not pre-mapped by the core; incorrect cookie handling can leak DMA mappings.

## Test Signals

Tests should cover GX and AXG compatibles, clock tree registration and rate changes, DDR and non-DDR timing, descriptor-chain and bounce-buffer paths, DRAM access quirk with aligned and rejected unaligned SGs, SBC/main/stop sequencing, SDIO IRQ disable/ack/reenable, tuning success/failure windows, regulator voltage switch, card busy reads, GPIO card-detect IRQs, and timeout/CRC error recovery with descriptor stop polling.
