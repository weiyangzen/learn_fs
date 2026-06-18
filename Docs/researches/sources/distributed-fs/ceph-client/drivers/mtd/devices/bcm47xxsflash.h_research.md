## sources/distributed-fs/ceph-client/drivers/mtd/devices/bcm47xxsflash.h

Purpose: private header for the BCMA serial flash driver. It defines controller opcode constants, status bits, the 16 MiB direct window size, supported flash-type enum, and `struct bcm47xxsflash`.

Important APIs, types, and functions: ST opcodes include write-enable, status read, page program, sector erase, subsector erase, and 4-byte read. Atmel opcodes cover buffer load/write/program, page/block erase, status, and compare/reprogram operations. `struct bcm47xxsflash` stores BCMA ChipCommon pointer, register access callbacks, flash type, MMIO window, geometry, and embedded `mtd_info`.

Control flow: no executable code. Constants are consumed by `bcm47xxsflash.c` command helpers and MTD operations.

State and persistence: state layout is the driver-private structure; media persistence is external flash content.

Dependencies and integration points: includes `linux/mtd/mtd.h` and forward-declares `struct bcma_drv_cc`. It is local to the BCMA serial flash implementation.

Risks: opcode values are controller-encoded rather than raw SPI opcodes in several cases, so reuse outside this driver would be unsafe. Adding flash types requires updates to both the enum and status/write/erase logic.

Test signals: build coverage for all constants used by the C file, correct geometry fields from BCMA platform data, and compile-time detection of struct/API drift.
