<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/otp.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/otp.c

Purpose: Shared SPI NAND OTP/protected-register support for factory and user one-time-programmable regions.

Important APIs/types/functions: Exposes `spinand_otp_page_size()`, `spinand_fact_otp_size()`, `spinand_user_otp_size()`, `spinand_fact_otp_read()`, `spinand_user_otp_read()`, `spinand_user_otp_write()`, and `spinand_set_mtd_otp_ops()`. Internal helpers include bound checks, `spinand_otp_rw()`, MTD OTP info/read/write/erase/lock wrappers, and mutex-protected dispatch.

Control flow: Size helpers compute pages times page+OOB size. Generic OTP read/write validates bounds, enables `CFG_OTP_ENABLE`, builds raw `nand_page_io_req` requests starting at layout start page plus offset-derived page, loops page by page through `spinand_read_page()` or `spinand_write_page()`, updates `retlen`, and disables OTP mode. `spinand_set_mtd_otp_ops()` maps vendor-provided factory/user ops into MTD protected register callbacks.

State and persistence: Runtime state is only stack request state and `retlen`; operation serialization uses the SPI NAND mutex in MTD wrappers. Persistent state is chip OTP content and vendor lock/protect state. The helper temporarily toggles OTP mode in the chip configuration.

Dependencies/integration: Depends on SPI NAND core page I/O and config helpers, `struct spinand_fact_otp_ops`, `struct spinand_user_otp_ops`, MTD protected register callbacks, and vendor layouts supplied in `spinand_info`.

Risks: `spinand_otp_rw()` uses raw page mode and casts const away for writes, so devices without raw access or with special OTP ECC rules need vendor overrides. Clearing OTP mode failure converts the operation to `-EIO` after bytes may have been transferred. Bounds use `ofs + len`, which can overflow for extreme inputs if not constrained by caller types.

Test signals: MTD user/factory protected register info/read/write/lock/erase operations, zero-length calls, unaligned offsets spanning pages, bounds failures, OTP mode cleanup on errors, and vendor-specific OTP devices such as Micron and ESMT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/spi/otp.c -->
