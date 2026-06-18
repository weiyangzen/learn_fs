<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.c

### Purpose
`common.c` implements shared Orion5x SoC initialization: IO mapping, fixed TCLK registration, platform-device setup, MBUS windows, timer init, SoC identification, restart, and memory-tag fixups.

### Important APIs, Types, And Functions
Public APIs include `orion5x_map_io()`, `clk_init()`, peripheral init helpers, `orion5x_init_early()`, `orion5x_setup_wins()`, `orion5x_timer_init()`, `orion5x_id()`, `orion5x_init()`, `orion5x_restart()`, and `tag_fixup_mem32()`.

### Control Flow
Early init sets timer base and initializes MBUS based on detected device ID. Main init prints SoC ID/TCLK, programs PCIe/PCI windows, registers the clock root, applies the 5281 D0 WFI workaround, conditionally registers crypto with SRAM MBUS window, and registers the watchdog. Timer init derives TCLK from device ID/reset sample and calls `orion_time_init()`.

### State, Persistence, And Dependencies
Persistent state includes static IO mappings, global `orion5x_tclk`, registered clocks/devices, MBUS address windows, and optional CPU idle polling mode. Dependencies include plat-orion helpers, MVEBU MBUS, platform device APIs, bridge registers, and PCIe ID access.

### Integration Points
Every ATAGS board file and DT machine path calls these helpers for shared SoC bring-up.

### Risks
MBUS and IO window programming is foundational; mistakes break PCI, device bus, crypto SRAM, and peripherals. Restart assumes reset output and CPU soft reset registers behave. Memory tag fixup mutates bootloader ATAGs and must avoid clearing valid RAM.

### Test Signals
Board boot should show correct Orion ID/TCLK, working serial/timer/IRQ, registered watchdog, correct crypto availability, and successful soft restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/common.c -->
