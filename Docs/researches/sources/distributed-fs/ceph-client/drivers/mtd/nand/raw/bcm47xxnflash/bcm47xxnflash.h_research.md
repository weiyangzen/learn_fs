# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/bcm47xxnflash.h

Purpose: private shared header for the BCM47xx NAND driver.

Important APIs/types/functions: `struct bcm47xxnflash` stores the BCMA ChipCommon pointer, embedded `nand_chip`, current legacy command, current page and column, and an 8-byte READID cache. It declares `bcm47xxnflash_ops_bcm4706_init`.

Control flow: none. `main.c` allocates the state and calls the BCM4706 initializer, while `ops_bcm4706.c` uses the state to emulate legacy NAND command sequencing.

State and persistence: `curr_command`, `curr_page_addr`, and `curr_column` persist command context between legacy callbacks. `id_data` caches READID bytes because the hardware requires controlled chip-select assertion across a known sequence.

Dependencies/integration: internal to `bcm47xxnflash`; depends on MTD and raw NAND types.

Risks/test signals: stale command/column state and fixed ID cache length. Test READID, STATUS, page/OOB read, erase, program, and callback sequencing.
