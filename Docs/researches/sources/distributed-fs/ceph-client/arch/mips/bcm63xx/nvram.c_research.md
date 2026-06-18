# sources/distributed-fs/ceph-client/arch/mips/bcm63xx/nvram.c

Purpose: parses Broadcom 963xx NVRAM from boot flash into a safe in-kernel copy.

Important APIs and functions: `bcm63xx_nvram_init()` copies the NVRAM block, checks CRC32, and reports validity. `bcm63xx_nvram_get_name()` returns the board name. `bcm63xx_nvram_get_mac_address()` hands out sequential MAC addresses from the base address while avoiding invalid data. `bcm63xx_nvram_get_psi_size()` returns configured PSI size or a default.

Control flow: board PROM init calls the parser with a flash address. Later board registration asks for board name and device MACs.

State and persistence: keeps a static copy of NVRAM and a runtime MAC counter. It reads flash data but does not write flash.

Dependencies and integration points: integrates CFE/NVRAM layout, board detection, Ethernet registration, and kernel CRC/MAC validation helpers.

Risks and test signals: bad CRC or invalid MAC data can suppress device registration or generate wrong addresses. Test boot logs, board-name detection, MAC uniqueness, and fallback PSI behavior.
