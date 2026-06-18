<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.c

**Purpose:** `sclp_ftp.c` implements the LPAR SCLP Event Type 7 Diagnostic Test FTP transport for HMC drive file operations.

**Important APIs and functions:** Public functions are `sclp_ftp_startup()`, `sclp_ftp_shutdown()`, and `sclp_ftp_cmd()`. `sclp_ftp_et7()` builds and submits the outgoing Diagnostic Test FTP SCCB. `sclp_ftp_txcb()` completes the accepted-write request, while `sclp_ftp_rxcb()` handles the asynchronous ET7 completion event and copies result fields into globals.

**Control flow, state, and persistence:** `sclp_ftp_cmd()` initializes a global receive completion, submits the FTP request, waits for the SCLP command to be accepted, then waits unconditionally for the asynchronous FTP completion event. Result globals store load flag, file size, and transferred length because the incoming event buffer belongs to the SCLP core. Return flags map to byte count, `-EPERM`, `-EBUSY`, `-ENOENT`, or `-EIO`. The header explicitly documents non-reentrancy; callers must serialize.

**Dependencies and integration:** It depends on `hmcdrv_ftp.h`, `sclp_diag.h`, SCLP event registration for `EVTYP_DIAG_TEST`, physical addresses for buffers, and real-space ASCE settings.

**Risks and test signals:** Risks include indefinite wait because ET7 cannot be canceled, global result races if callers do not serialize, filename truncation/validation, unsupported event masks, and physical buffer-address validity. Tests should cover startup/shutdown registration, no-op probe, each FTP command, all load-flag mappings, timeout watchdogs at caller level, and concurrent-call exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_ftp.c -->
