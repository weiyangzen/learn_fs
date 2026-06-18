<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/esmt.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/esmt.c

Purpose: ESMT SPI NAND support, including devices that report either ESMT manufacturer ID `0x8c` or GigaDevice-like ID `0xc8`, plus ESMT-specific OOB and OTP handling.

Important APIs/types/functions: Defines `f50l1g41lb_ooblayout_ecc()`, `f50l1g41lb_ooblayout_free()`, OTP info callbacks, `f50l1g41lb_otp_lock()`, user/factory OTP ops, `esmt_8c_spinand_table`, `esmt_c8_spinand_table`, and two exported manufacturer descriptors.

Control flow: Core matches either manufacturer descriptor, installs the ESMT OOB layout, and for selected chips attaches user/factory OTP ops. OTP lock enters OTP/protect mode through config bits, performs write-enable and program-execute sequence, waits for completion, checks program-fail, then clears OTP mode.

State and persistence: No private allocation. Persistent state includes OTP pages and lock/protect bits in the chip configuration. The OOB layout intentionally exposes only small non-ECC-protected free chunks because some filesystems partially program OOB cleanmarkers.

Dependencies/integration: Uses SPI-MEM operations directly in the OTP lock path and shared SPI NAND OTP helpers from `otp.c`. Integrated through both `esmt_8c_spinand_manufacturer` and `esmt_c8_spinand_manufacturer` in `core.c`.

Risks: `f50l1g41lb_otp_lock()` appears to return early when `spinand_upd_cfg()` succeeds, so the later write-enable/program path is unreachable on that success path; that deserves scrutiny against upstream intent. The function also treats successful `spi_mem_exec_op()` calls as a jump to cleanup in two places, which is suspicious control flow. ESMT ID overlap with GigaDevice requires careful table ordering and IDs.

Test signals: Probe all ESMT IDs, verify OOB free/ECC bytes, read/write factory/user OTP where supported, test OTP lock persistence after power cycle, validate status/prog-fail handling, and run JFFS2/UBI OOB cleanmarker scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/esmt.c -->
