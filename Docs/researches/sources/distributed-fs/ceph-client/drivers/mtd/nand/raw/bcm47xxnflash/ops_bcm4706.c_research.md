# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/ops_bcm4706.c

Purpose: BCM4706-specific NAND operations over BCMA ChipCommon NFLASH registers. It uses legacy raw NAND callbacks because this hardware's command/address/data sequencing does not map cleanly to default helpers.

Important APIs/types/functions: `bcm47xxnflash_ops_bcm4706_ctl_cmd`, `bcm47xxnflash_ops_bcm4706_poll`, `bcm47xxnflash_ops_bcm4706_read`, and `bcm47xxnflash_ops_bcm4706_write` handle control/data movement. Legacy callbacks implement `cmd_ctrl`, `select_chip`, `dev_ready`, `cmdfunc`, `read_byte`, `read_buf`, and `write_buf`. `bcm47xxnflash_ops_bcm4706_init` installs callbacks, enables NAND, programs waits, scans, and configures geometry.

Control flow: initializer enables NAND access, derives wait counters from package option or PLL, scans NAND, validates power-of-two size, calculates row/column bytes, and writes `BCMA_CC_NFLASH_CONF`. Runtime `cmdfunc` records column/page and handles RESET, READID, STATUS, OOB, erase, sequence-in, and program commands.

State and persistence: current command/page/column and cached ID bytes live in `struct bcm47xxnflash`; hardware state includes wait counters, config, and row/column registers. ECC is disabled and BBT is stored in flash.

Dependencies/integration: BCMA ChipCommon registers, raw NAND legacy callbacks, and local header.

Risks/test signals: word-aligned buffer assumptions, no ECC, unsupported commands, fixed retry loops, READID caching, and geometry derivation. Test READID, STATUS, full page/OOB read, erase, program, and failure cleanup disabling NAND access.
