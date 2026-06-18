# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_board.h

**Purpose:** Declares BCM63xx board-level initialization entry points.

**Important APIs/types/functions:** Exports `board_get_name()`, `board_prom_init()`, `board_setup()`, and `board_register_devices()`.

**Control flow:** Boot code calls PROM init, board setup, and device registration to convert NVRAM/board data into platform devices and machine state. `board_get_name()` exposes the selected board identity.

**State and persistence behavior:** No state in the header. Implementations initialize persistent boot-time board configuration, platform resources, and device registration state.

**Dependencies and integration points:** Integrated by BCM63xx arch init, NVRAM, flash, GPIO, Ethernet, PCI, UART, SPI, and USB registration paths.

**Risks:** Ordering is critical: devices registered before board/NVRAM setup can receive incomplete resources. Board name mismatches can select wrong quirks.

**Test signals:** Boot boards with known NVRAM, verify board name, platform-device list, resource ranges, and failure behavior when device registration returns errors.
