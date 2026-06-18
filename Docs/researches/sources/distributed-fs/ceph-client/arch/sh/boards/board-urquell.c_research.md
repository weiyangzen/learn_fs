<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-urquell.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-urquell.c

Purpose: This file supports the Urquell SH7786 board with heartbeat LEDs, SMC91x Ethernet, NOR flash, power-off behavior, IRQ setup, mode pins, clock initialization, and the machine vector.

Important APIs/types/functions: It defines heartbeat resource/device, SMC91x platform data/resources/device, NOR flash partitions/data/resources/device, `urquell_devices`, `urquell_devices_setup`, `urquell_power_off`, `urquell_init_irq`, `urquell_mode_pins`, `urquell_clk_init`, `urquell_setup`, and `mv_urquell`.

Control flow: Device init registers board devices. Setup installs power-off handling and board-specific initialization. Clock/IRQ/mode-pin callbacks are provided through the machine vector.

State and persistence: Static platform tables persist for Ethernet, flash, and heartbeat. Power-off handler and clock setup affect global platform behavior. Flash partitions define persistent storage layout.

Dependencies and integration points: It depends on SH7786 CPU support, SMC91x Ethernet, physmap flash, heartbeat driver, clock and IRQ helpers, PCI/no-ioport-map behavior from Kconfig, and SuperH machvec.

Risks and test signals: Ethernet/flash hard-coded resource windows and power-off register behavior must match board wiring. Tests include boot, Ethernet traffic, flash partition visibility, heartbeat, power-off, clock setup, and mode-pin reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-urquell.c -->
