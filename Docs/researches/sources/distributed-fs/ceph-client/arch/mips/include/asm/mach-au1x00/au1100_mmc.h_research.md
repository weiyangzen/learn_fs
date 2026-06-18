# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-au1x00/au1100_mmc.h

**Purpose:** Provides register offsets, bit definitions, and board platform data for the Au1100/Au1x MMC/SD controller driver.

**Important APIs/types/functions:** Defines `struct au1xmmc_platform_data` with card-detect setup/status, read-only, power control, LED, and host-capability mask hooks. Exports `SD0_BASE`, `SD1_BASE`, register offsets such as `SD_TXPORT`, `SD_RXPORT`, `SD_CONFIG`, `SD_ENABLE`, `SD_BLKSIZE`, `SD_STATUS`, `SD_CMD`, response and timeout registers, plus masks for config/status FIFO, command, response, block size/count, and enable bits.

**Control flow:** Board code supplies callbacks, the MMC driver programs clock/divider and enable bits, issues commands through `SD_CMDARG`/`SD_CMD`, transfers data through TX/RX ports or DMA, watches status bits, and calls board hooks for power/card state.

**State and persistence behavior:** The header owns no state. Runtime state is in controller registers and board callback side effects such as card power, LED state, and host capabilities.

**Dependencies and integration points:** Depends on `<linux/leds.h>` and the MMC core driver. Integrates with Alchemy address definitions, GPIO/card-detect hardware, and board-specific power control.

**Risks:** Register masks include reserved/placeholder fields and direct physical base constants, so mismatched controller revisions can fail silently. Board callbacks receive opaque `mmc_host` pointers, making type misuse possible. Wrong block count/size or status handling can corrupt transfers.

**Test signals:** Probe both slots where present, test card insertion/removal, read-only detection, power cycling, LED behavior, PIO/DMA transfers, timeout/error reporting, and broad MMC/SD card compatibility.
