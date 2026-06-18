# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/samsung.h

## Purpose
`samsung.h` is the private register/bit definition header for the Samsung OneNAND controller driver. It gives `onenand_samsung.c` symbolic offsets for controller registers and interrupt/error bits.

## Important APIs, Types, and Functions
The file defines no functions or structs. Register offsets include memory configuration, burst length, reset, interrupt/error status/mask/acknowledge, ECC status, manufacturer/device IDs, buffer sizes, technology, address-width registers, transfer-spare control, interrupt pin enable, access clock, flash version ID, and an S3C64xx auxiliary control offset. It also defines reset command values and status bits such as `CACHE_OP_ERR`, `RST_CMP`, `RDY_ACT`, `INT_ACT`, `UNSUP_CMD`, `LOCKED_BLK`, `BLK_RW_CMP`, `ERS_CMP`, `PGM_CMP`, `LOAD_CMP`, `ERS_FAIL`, `PGM_FAIL`, `INT_TO`, `LD_FAIL_ECC_ERR`, and `TSRF`.

## Control Flow
There is no runtime control flow in the header. The constants drive control flow in `onenand_samsung.c`: reset waits for `RST_CMP`, wait paths look for `LOAD_CMP` / `PGM_CMP` / `ERS_CMP` / `BLK_RW_CMP`, ECC/error paths inspect `LD_FAIL_ECC_ERR`, lock failures use `LOCKED_BLK`, and OOB transfer toggles `TSRF`.

## State and Persistence
The header itself stores no state. Its offsets address volatile controller registers whose writes can trigger persistent flash operations such as erase, program, and lock/unlock when used by the driver.

## Dependencies and Integration Points
It is included only by the Samsung OneNAND platform driver. It depends on the controller hardware layout remaining consistent with S3C64xx/S5PC1xx expectations.

## Risks
Incorrect offsets or bit definitions would directly break probing, wait completion, ECC/error handling, and spare-area transfer. Because these macros are untyped and shared across SoC variants, variant-specific differences must be handled in the C driver rather than here.

## Test Signals
Compile coverage comes through `onenand_samsung.c`. Runtime signals are correct device ID reads, reset completion, accurate interrupt acknowledgement, ECC error reporting, and successful spare-area transfers.
