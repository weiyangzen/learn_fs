<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.h

**Purpose:** This header declares the SCLP ET7 FTP backend interface used by the HMC drive FTP abstraction when running on LPAR.

**Important APIs and types:** It includes `hmcdrv_ftp.h` for `struct hmcdrv_ftp_cmdspec` and declares `sclp_ftp_startup()`, `sclp_ftp_shutdown()`, and `sclp_ftp_cmd(const struct hmcdrv_ftp_cmdspec *ftp, size_t *fsize)`.

**Control flow, state, and persistence:** The header warns that all exported functions are non-reentrant and require exclusive caller-side serialization. The `fsize` out parameter returns the full remote file size when the backend reports it, while the function return value is the actual bytes transferred or a negative errno.

**Dependencies and integration:** It is consumed by the HMC drive transport layer and implemented by `sclp_ftp.c`. The backend relies on SCLP event registration and Diagnostic Test event buffers.

**Risks and test signals:** Risks include callers treating the API as reentrant, ignoring the separate transferred-length and file-size semantics, or calling before startup. Test signals are serialized command execution, unsupported-backend behavior, correct file-size reporting on GET/DIR-like operations, and clean unregister during shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.h -->
