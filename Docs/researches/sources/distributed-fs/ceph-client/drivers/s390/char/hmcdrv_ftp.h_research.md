<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_ftp.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_ftp.h

**Purpose:** This header defines the common HMC drive FTP service contract used by the s390 HMC DVD access stack. It is not a transport implementation; it supplies the command IDs, request descriptor, path-length limit, and public entry points that higher-level cache/device code and lower-level FTP backends share.

**Important APIs and types:** `HMCDRV_FTP_FIDENT_MAX` limits null-terminated file identifiers to 192 bytes. `enum hmcdrv_ftp_cmdid` covers probe/no-op, read, write, append, long directory listing, name listing, delete, and cancel. `struct hmcdrv_ftp_cmdspec` carries command ID, file offset, ASCII filename, kernel transfer buffer, and byte count. Exported prototypes are `hmcdrv_ftp_startup()`, `hmcdrv_ftp_shutdown()`, `hmcdrv_ftp_probe()`, `hmcdrv_ftp_do()`, and user-facing `hmcdrv_ftp_cmd()`.

**Control flow, state, and persistence:** The header is stateless, but its descriptor defines the transactional unit for HMC file operations. Callers must provide a kernel buffer that satisfies the backend alignment expectations documented here, especially the 4 KiB alignment note for `buf`.

**Dependencies and integration:** It depends only on Linux scalar types and is included by `hmcdrv_mod.c` and `sclp_ftp.c`. The command set maps directly onto SCLP Diagnostic Test FTP in the LPAR backend.

**Risks and test signals:** Main risks are ABI mismatch between cache/device layers and the selected backend, filename truncation, unaligned buffers, and incorrect interpretation of transfer lengths versus file size. Useful tests include probe/no-op on supported and unsupported machines, boundary-length filenames, zero-length transfers, offset reads, and all command IDs returning expected errno mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/hmcdrv_ftp.h -->
