## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw.c

### Purpose
`ivpu_hw.c` provides generation-independent hardware orchestration for platform detection, workarounds, timeouts, memory ranges, power up/down, firmware boot, IRQ dispatch, profiling clock choice, and ECC MCA signaling.

### Important APIs, Types, And Functions
Public functions include `ivpu_hw_init()`, `ivpu_hw_range_init()`, `ivpu_hw_power_up()`, `ivpu_hw_power_down()`, `ivpu_hw_reset()`, `ivpu_hw_boot_fw()`, `ivpu_hw_profiling_freq_drive()`, `ivpu_irq_handlers_init()`, `ivpu_hw_irq_enable()`, `ivpu_hw_irq_disable()`, `ivpu_hw_irq_handler()`, and `ivpu_hw_uses_ecc_mca_signal()`. Internal helpers initialize platform, workarounds, timeouts, priority bands, and memory ranges.

### Control Flow
Hardware init reads buttress info/fuses/frequencies, sets HWS priority defaults, initializes VPU address ranges by IP generation, reads platform, initializes workarounds and timeouts, and prepares optional fault injection. Power-up disables D0i3, enables workpoint/PLL, applies LNL clock/profiling/ATS setup, configures host SS, disables idle generation, waits clock ownership, powers the IP domain, enables AXI and top NoC, and writes LNL arbitration weights. Power-down saves D0i3 timestamps, warns if not idle, resets IP, disables workpoint, and enters D0i3. IRQ handling globally masks buttress interrupts, dispatches buttress then IP handlers, reenables global interrupts, and marks PM activity.

### State, Persistence, And Dependencies
Hardware state includes PLL/workpoint, power islands, D0i3 timestamps, platform, workarounds, timeout values, address ranges, IRQ handler function pointers, and firewall IRQ counter. Dependencies include buttress/IP helper layers, PM runtime, MSR reads for ECC, DMI/fault injection headers, and module test parameters.

### Integration Points
`ivpu_drv.c` calls this during device init, boot, shutdown, and IRQ handling. Firmware boot params consume ranges, PLL ratios, telemetry, and ECC signaling. Debugfs can alter profiling frequency and fault injection.

### Risks
Power sequencing is strict and generation-sensitive. Workarounds can be forced by test mode and may change power/clock behavior. IRQ dispatch skips IP handling when hardware is idle and buttress handled the interrupt, which relies on accurate idle status. Memory range differences between 37xx and newer generations affect every BO mapping.

### Test Signals
Test hardware init on each PCI ID/revision/platform, range boundaries, power-up/power-down/reset error injection, IRQ paths for buttress/IP/no interrupt, profiling frequency toggles, D0i3 timestamp propagation to warm boot, and ECC MCA MSR behavior on 50xx+.
