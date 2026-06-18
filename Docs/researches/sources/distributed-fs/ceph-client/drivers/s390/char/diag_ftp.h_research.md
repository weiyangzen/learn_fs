# sources/distributed-fs/ceph-client/drivers/s390/char/diag_ftp.h

Purpose: declares the DIAG X'2C4' HMC FTP backend interface.

Important APIs/types/functions: declares `diag_ftp_startup()`, `diag_ftp_shutdown()`, and `diag_ftp_cmd(const struct hmcdrv_ftp_cmdspec *, size_t *)`.

Control flow: no runtime flow. The header marks backend functions as non-reentrant in comments, leaving serialization to callers.

State and persistence behavior: no state in the header.

Dependencies and integration points: includes `hmcdrv_ftp.h` and is consumed by `hmcdrv_ftp.c` to select z/VM transfer operations.

Risks and test signals: compile-time contract must stay aligned with `diag_ftp.c` and `hmcdrv_ftp.c`; test z/VM backend builds with `CONFIG_HMC_DRV`.
