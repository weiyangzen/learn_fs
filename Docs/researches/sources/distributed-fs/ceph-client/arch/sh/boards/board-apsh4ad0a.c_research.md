<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-apsh4ad0a.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-apsh4ad0a.c

Purpose: This board file initializes the ALPHAPROJECT AP-SH4AD-0A platform with SMSC911x Ethernet, dummy regulators, clock setup, IRQ setup, mode-pin decoding, and machine-vector registration.

Important APIs/types/functions: It defines dummy SMSC911x supplies, SMSC911x resources/config/device, `apsh4ad0a_devices`, `apsh4ad0a_devices_setup`, `apsh4ad0a_mode_pins`, `apsh4ad0a_clk_init`, `apsh4ad0a_setup`, `apsh4ad0a_init_irq`, and `mv_apsh4ad0a`.

Control flow: The device initcall registers fixed regulators and the Ethernet platform device. Clock/setup/IRQ/mode-pin callbacks are attached through the machine vector for the SH7786-based board.

State and persistence: Persistent state is static platform data/resources and machine-vector callbacks. Mode-pin reads reflect hardware strap state.

Dependencies and integration points: It depends on SH7786 CPU support, SuperH interrupt and clock setup, fixed regulators, and the SMSC911x platform driver.

Risks and test signals: Ethernet resource windows and IRQ polarity/type must match the board. Tests include board boot, SMSC911x network bring-up, fixed-regulator availability, and mode-pin reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-apsh4ad0a.c -->
