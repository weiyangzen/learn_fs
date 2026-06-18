<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/micron.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/micron.c

Purpose: Micron SPI NAND table and special handling for multi-die selection, Micron ECC status encoding, OOB layouts, and MT29F2G01ABAGD OTP regions.

Important APIs/types/functions: Defines manufacturer ID `0x2c`, Micron ECC status masks, `micron_8_ooblayout`, `micron_4_ooblayout`, `micron_select_target()`, `micron_8_ecc_get_status()`, `mt29f2g01abagd_otp_is_locked()`, OTP info/lock ops, `micron_spinand_table`, `micron_spinand_init()`, and exported `micron_spinand_manufacturer`.

Control flow: Core matches Micron IDs, installs x1/x4/quadio cache variants, attaches target selection for multi-die parts, sets OTP descriptors for ABAGD, and calls manufacturer init. Target selection writes the die-select register. OTP info reads the first user OTP page to infer lock state, while OTP lock sets config OTP/lock bits and uses shared read/write helpers.

State and persistence: Runtime state is descriptor-driven with no large private object. Persistent state includes selected die register, OTP pages and lock state, feature/config bits, and OOB metadata. OOB layouts differ between 4-bit and 8-bit ECC generations.

Dependencies/integration: Uses shared `otp.c` helpers, SPI NAND register helpers, MTD OOB callbacks, and `SPINAND_SELECT_TARGET` so core target changes call Micron logic.

Risks: Multi-target parts must reliably switch die before reads/writes/erases; stale target selection risks cross-die corruption. OTP lock-state detection depends on reading a page pattern and can be sensitive to raw-read support and ECC mode. ECC decoder returns range upper bounds, so wear layers may react conservatively.

Test signals: Multi-die read/write/erase across target boundaries, OTP info/read/write/lock persistence, Micron ECC status decoding for 1-3/4-6/7-8/uncorrectable, OOB layout tests, and init behavior for parts requiring quad enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/micron.c -->
