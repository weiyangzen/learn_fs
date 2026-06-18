<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.c

**Purpose:** This file implements the SCLP Control Program Identification interface, exposing sysfs knobs and an exported helper for sending system identity data to firmware/HMC.

**Important APIs and functions:** `sclp_cpi_set_data()` is exported for in-kernel callers. Sysfs attributes under `/sys/firmware/cpi/` include `system_name`, `sysplex_name`, `system_type`, `system_level`, and write-only `set`. `cpi_prepare_req()` builds the CPI event SCCB, `cpi_req()` registers the event, submits the request, waits for completion, checks response code `0x0020`, then unregisters.

**Control flow, state, and persistence:** Global identity fields are protected by `sclp_cpi_mutex`. String stores validate length and allowed characters, uppercase and blank-pad to eight bytes, and leave changes in memory until `set` or `sclp_cpi_set_data()` sends them. The request path translates fields to SCLP EBCDIC representation and uses a transient DMA page.

**Dependencies and integration:** It uses SCLP Write Event Data with event type `EVTYP_CTLPROGIDENT`, completion callbacks, firmware ksets, sysfs attributes, EBCDIC conversion, and the SCLP mask registration system.

**Risks and test signals:** Risks include sysfs values not being null-terminated display strings after blank padding, registration overhead on every send, unsupported firmware send mask, and identity validation being stricter than user expectations. Tests should cover valid/invalid characters, newline stripping, level hex parsing, unsupported event type, request status failure, and concurrent sysfs/API updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.c -->
