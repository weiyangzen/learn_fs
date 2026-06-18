# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-bcm63xx/bcm63xx_nvram.h

**Purpose:** Declares BCM63xx NVRAM initialization and accessors for board identity, MAC addresses, and PSI size.

**Important APIs/types/functions:** Exports `bcm63xx_nvram_init(void *nvram)`, `bcm63xx_nvram_get_name()`, `bcm63xx_nvram_get_mac_address(u8 *mac)`, and `bcm63xx_nvram_get_psi_size()`. Comments document checksum validation, a 16-byte board-name field that may not be null-terminated, and monotonic allocation of MAC addresses from NVRAM.

**Control flow:** Early boot copies and validates NVRAM from the provided address, board code reads the board name, device registration requests MAC addresses, and storage/flash code reads PSI size.

**State and persistence behavior:** Implementation keeps a local NVRAM copy and tracks allocated MAC addresses. NVRAM represents persistent board configuration stored in flash.

**Dependencies and integration points:** Depends on Linux types. Integrated by board detection, Ethernet registration, flash/partition layout, and bootloader-provided NVRAM location.

**Risks:** Board name may lack a terminator, so string users must bound copies. Bad checksum or malformed MAC pool can break board detection/network identity. Repeated MAC allocation changes results by call order.

**Test signals:** Boot with valid and invalid NVRAM, verify checksum handling, bounded board-name use, deterministic MAC allocation across devices, PSI size parsing, and fallback behavior for missing fields.
