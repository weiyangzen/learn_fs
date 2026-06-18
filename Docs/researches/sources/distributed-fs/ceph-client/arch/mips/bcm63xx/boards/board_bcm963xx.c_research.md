# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/boards/board_bcm963xx.c

Purpose: board database and staged board initialization for legacy Broadcom 963xx/BCM63xx reference and ISP router boards.

Important APIs and functions: static `struct board_info` records board names, expected CPU IDs, UART/PCI/PCMCIA/USB/Ethernet flags, LED tables, and optional reset GPIOs. `board_prom_init()` reads boot flash/CFE/NVRAM or HCS board names, selects a board descriptor, initializes PCI and pinmux hints, and copies the selected descriptor out of `__initdata`. `board_setup()` validates a board was found and that the CPU ID matches. `board_register_devices()` registers UART, PCMCIA, Ethernet, USB device, SSB fallback SPROM, SPI/HSSPI, flash, GPIO LEDs, and optional EPHY reset GPIO. `board_get_name()` exposes the selected board name.

Control flow: boot proceeds in three stages: early PROM board identification, second-stage validation once early printk is available, and later platform-device registration. Device registration is conditional on fields in the selected `board_info` and MAC address allocation from NVRAM.

State and persistence: the global `board` struct is the durable in-kernel copy for the boot. It reads CFE version, NVRAM board name, MAC addresses, and PSI metadata from flash, but writes only kernel platform-device state and GPIO/pinmux registers.

Dependencies and integration points: integrates CFE/NVRAM layout, BCM63xx CPU helpers, GPIO mode registers, PCI enable state, Ethernet/flash/UART/SPI/HSSPI/PCMCIA/USBD registration helpers, GPIO LED subsystem, and SSB fallback SPROM for PCI WLAN.

Risks and test signals: board matching uses 16-byte names and hard-coded descriptors, so unknown or mistyped boards panic later or miss devices. MAC allocation failure suppresses Ethernet registration. Test signals include CFE version log, `board name` log, registered platform devices, correct LEDs, Ethernet MAC uniqueness, PCI WLAN SPROM behavior, and successful boot on each CPU family.
