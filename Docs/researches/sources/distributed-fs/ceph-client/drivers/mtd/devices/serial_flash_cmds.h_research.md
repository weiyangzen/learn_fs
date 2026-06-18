# sources/distributed-fs/ceph-client/drivers/mtd/devices/serial_flash_cmds.h

Purpose: small shared header defining serial flash opcodes and feature flags used by legacy serial flash controller drivers, notably `st_spi_fsm.c`.

Important APIs/types/functions: command definitions include volatile configuration register opcodes `SPINOR_OP_WRVCR`/`SPINOR_OP_RDVCR` and several JEDEC/SFDP page-program opcodes for single, dual, and quad I/O widths. Feature masks group capabilities into single, dual, and quad read/write flags plus erase/chip erase, 32-bit address, reset, and DYB locking flags.

Control flow: no executable flow. Drivers use the flags to choose preferred command sequences by testing whether a flash table entry supports a candidate read/write mode.

State and persistence: no state. The flags describe persistent hardware capabilities and supported command sets; they do not store runtime state.

Dependencies/integration: protected by `_MTD_SERIAL_FLASH_CMDS_H`. It intentionally complements standard `linux/mtd/spi-nor.h` command definitions with older driver-local capability flags.

Risks: capability bits are local conventions; mixing them with other SPI NOR capability schemes can misconfigure command widths. Some opcode names overlap vendor-specific meanings, so users must interpret them through the target chip table.

Test signals: compile coverage from consumers, especially sequence selection in `st_spi_fsm.c`, and table entries choosing expected commands for single/dual/quad modes.
