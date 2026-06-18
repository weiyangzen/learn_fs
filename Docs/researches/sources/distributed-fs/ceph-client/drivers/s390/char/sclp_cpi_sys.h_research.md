<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.h

**Purpose:** This header exposes the in-kernel CPI helper for setting and sending SCLP control program identification data.

**Important APIs and types:** The single declaration is `sclp_cpi_set_data(const char *system, const char *sysplex, const char *type, u64 level)`. The strings correspond to the sysfs `system_name`, `sysplex_name`, and `system_type` fields, while `level` is the 64-bit system level sent in the CPI event.

**Control flow, state, and persistence:** The header is stateless. Its function mutates the global CPI identity state in `sclp_cpi_sys.c` and immediately sends a CPI request under that file's mutex.

**Dependencies and integration:** It depends only on `u64` being visible through included kernel types in consumers. In-tree users can avoid sysfs by calling the exported symbol directly.

**Risks and test signals:** Risks are mainly caller-side: passing strings longer than eight accepted characters, invalid characters, or calling before SCLP CPI sysfs initialization on platforms where the event type is unsupported. Test signals are exported symbol resolution, valid identity transmission, and expected `-EINVAL`, `-EOPNOTSUPP`, or `-EIO` return propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cpi_sys.h -->
