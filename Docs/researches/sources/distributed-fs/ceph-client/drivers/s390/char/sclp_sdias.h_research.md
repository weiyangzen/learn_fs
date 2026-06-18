<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.h

**Purpose:** This header defines the SDIAS event constants and packed SCCB/event-buffer layouts for SCLP store-data-in-absolute-storage dump support.

**Important APIs and types:** Constants define event qualifiers `SDIAS_EQ_STORE_DATA` and `SDIAS_EQ_SIZE`, data ID `SDIAS_DI_FCP_DUMP`, ASA size selectors, and event states `SDIAS_EVSTATE_ALL_STORED`, `SDIAS_EVSTATE_NO_DATA`, and `SDIAS_EVSTATE_PART_STORED`. `struct sdias_evbuf` contains event qualifier, data ID, event ID, ASA size/status, block count, absolute-storage address, first/last block, and data block size. `struct sdias_sccb` wraps it in an SCCB header.

**Control flow, state, and persistence:** The header is stateless. `sclp_sdias.c` fills these fields per request and stores asynchronous responses in the same structure shape.

**Dependencies and integration:** It includes `sclp.h` for `evbuf_header` and `sccb_header`. The layout is consumed by dump IPL code through `sclp_sdias.c`.

**Risks and test signals:** Risks include packed layout mismatch with firmware, confusion between block counts and byte counts, and status handling that treats partial storage as acceptable but reports no-data as failure. Tests should validate structure sizes/offsets, EQ_SIZE block-count response, copy request encoding, and event-status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_sdias.h -->
