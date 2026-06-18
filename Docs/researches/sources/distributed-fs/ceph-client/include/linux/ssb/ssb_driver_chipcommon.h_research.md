<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_chipcommon.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_chipcommon.h

Purpose: Defines ChipCommon core registers, capability bits, PLL/clock/PMU constants, GPIO/watchdog interfaces, and the `ssb_chipcommon` accessor surface for SSB chips.

Important APIs/types/functions: Hundreds of `SSB_CHIPCO_*` register and bitfield constants, `struct ssb_chipcommon`, `ssb_chipcommon_available()`, `chipco_read32/write32()`, mask/set helpers, `ssb_chipcommon_init()`, suspend/resume, clock query/timing functions, `enum ssb_clkmode`, `ssb_chipco_set_clockmode()`, watchdog setter, IRQ mask/status helpers, GPIO helpers, serial init, PMU init, LDO voltage and PA reference controls, and spur-avoid PLL update.

Control flow: Driver code probes ChipCommon availability through `cc->dev`, uses register accessor macros over SSB MMIO, initializes clocks/timing/PMU, and manipulates GPIO/IRQ/watchdog registers through typed helper functions.

State and persistence behavior: Hardware register state covers chip ID/capabilities, interrupt masks, flash/OTP/JTAG, GPIO, clock control, watchdog, and PMU resources. In-memory `ssb_chipcommon` points to the backing SSB device.

Dependencies: SSB MMIO wrappers, serial-port definitions from MIPS header when serial is enabled, PMU and GPIO subsystems, and chip revision-specific register semantics.

Integration points: Central integration for Broadcom SoC clocking, GPIO, serial, flash, PMU, watchdog, and board bring-up.

Risks: Register definitions are revision-sensitive; using GPIO/PMU/watchdog helpers without checking availability or capability bits can touch invalid hardware. Mask/set helpers perform read-modify-write and need proper locking at call sites.

Test signals: ChipCommon probe on multiple revisions, clock-mode transitions, GPIO read/write/IRQ tests, watchdog timer tests, PMU voltage/spur-avoid tests, and suspend/resume register preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_chipcommon.h -->
