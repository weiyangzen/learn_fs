# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm47xx/bcm47xx_board.h

**Purpose:** Enumerates known BCM47xx router/board models and declares board detection accessors.

**Important APIs/types/functions:** Defines `enum bcm47xx_board` with many ASUS, Belkin, Buffalo, Cisco/Linksys, Dell, D-Link, Huawei, Luxul, Microsoft, Motorola, Netgear, Phicomm, Siemens, SimpleTech, ZTE, plus `UNKNOWN` and `NO`. Exports `BCM47XX_BOARD_MAX_NAME`, `bcm47xx_board_detect()`, `bcm47xx_board_get()`, and `bcm47xx_board_get_name()`.

**Control flow:** Early board detection matches NVRAM/SPROM/model data to an enum, stores the result in implementation state, and later board-specific quirks or LEDs/buttons/devices branch on `bcm47xx_board_get()`.

**State and persistence behavior:** The header has no storage, but the implementation maintains detected board identity for the boot lifetime. Board identity effectively becomes platform configuration state.

**Dependencies and integration points:** Integrated with BCM47xx NVRAM parsing, board setup, LEDs/buttons, Ethernet, wireless calibration, flash layout, and user-visible machine name reporting.

**Risks:** Adding/removing/reordering enum values can break code that stores or compares numeric IDs internally. Board-name length limits can truncate model strings. Misdetecting a board can apply wrong GPIO, switch, LED, or flash quirks.

**Test signals:** Boot boards across vendor families, verify detected enum/name, compare against NVRAM model fields, test board-specific buttons/LEDs/network ports, and build-check every enum user after adding IDs.
