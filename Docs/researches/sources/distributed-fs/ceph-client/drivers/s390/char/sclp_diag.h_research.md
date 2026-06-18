<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_diag.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_diag.h

**Purpose:** This header defines the Diagnostic Test event-buffer layouts used by the SCLP ET7 FTP service.

**Important APIs and types:** Return flags include `SCLP_DIAG_FTP_OK`, `SCLP_DIAG_FTP_LDFAIL`, `SCLP_DIAG_FTP_LDNPERM`, `SCLP_DIAG_FTP_LDRUNS`, and `SCLP_DIAG_FTP_LDNRUNS`. `SCLP_DIAG_FTP_XPCX` and `SCLP_DIAG_FTP_ROUTE` identify the FTP service. `struct sclp_diag_ftp` contains command, offset, file size, transfer length, buffer address, ASCE, and 256-byte file identifier. `struct sclp_diag_evbuf` wraps model-dependent data by route, and `struct sclp_diag_sccb` wraps the event in an SCCB.

**Control flow, state, and persistence:** The header is stateless, but its packed layouts are copied directly to/from firmware-owned SCCBs. `SCLP_DIAG_FTP_EVBUF_LEN` computes the exact event length used by `sclp_ftp.c`.

**Dependencies and integration:** It depends on Linux types and the SCLP event/SCCB headers included before use. The layout is consumed by `sclp_ftp.c`.

**Risks and test signals:** Risks are hardware ABI drift, packing/alignment mistakes, different filename maximums between this 256-byte field and `HMCDRV_FTP_FIDENT_MAX`, and physical versus virtual buffer address confusion. Tests should validate event length, packed offsets, response flag mapping, and filename boundary handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_diag.h -->
