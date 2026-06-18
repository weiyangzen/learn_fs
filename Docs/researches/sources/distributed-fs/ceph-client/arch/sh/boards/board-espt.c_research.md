<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-espt.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/board-espt.c

Purpose: This file provides ESPT board support for SH7763 systems, defining NOR flash, SH Ethernet resources/platform data, device registration, and the machine vector.

Important APIs/types/functions: It defines NOR flash partitions/data/resources/device, `sh_eth_resources`, `sh7763_eth_pdata`, `espt_eth_device`, `espt_devices`, `espt_devices_setup`, and `mv_espt`.

Control flow: The device initcall registers flash and Ethernet devices. The machine vector identifies the board for the SuperH platform layer.

State and persistence: Static resource and platform-data tables persist for flash and Ethernet.

Dependencies and integration points: It depends on SH7763 CPU support, physmap flash, Renesas SH Ethernet platform driver, and platform-device registration.

Risks and test signals: Ethernet PHY/interface resources and flash partition offsets must match hardware. Tests include ESPT boot, MTD partition listing, Ethernet link/traffic, and IRQ/resource conflict checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/board-espt.c -->
