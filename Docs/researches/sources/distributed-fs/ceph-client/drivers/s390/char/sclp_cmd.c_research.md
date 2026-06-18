<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cmd.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cmd.c

**Purpose:** `sclp_cmd.c` contains synchronous command helpers for CPU core and channel-path information/reconfiguration.

**Important APIs and functions:** `sclp_sync_request()` and `sclp_sync_request_timeout()` allocate a `struct sclp_req`, install a completion callback, submit through `sclp_add_request()`, and wait. `_sclp_get_core_info()` reads CPU/core information. `sclp_core_configure()` and `sclp_core_deconfigure()` issue CPU configure command words. `sclp_chp_configure()`, `sclp_chp_deconfigure()`, and `sclp_chp_read_info()` manage channel paths.

**Control flow, state, and persistence:** All commands use transient DMA-capable SCCBs and block until callback completion. CPU info chooses extended SCCB length when facility 140 is available. Configure commands check capability bits before allocation, submit the command, validate hardware response codes, and free the SCCB. No durable state is stored here; callers own resulting core/channel-path info.

**Dependencies and integration:** It depends on the SCLP queue, completion API, s390 facility detection, channel-path IDs, and `sclp_fill_core_info()` from `sclp.h`. These functions are used by CPU hotplug and channel subsystem management.

**Risks and test signals:** Risks include synchronous waits hanging if the SCLP core never completes, response-code lists becoming stale, incorrect SCCB length under facility 140, and queue-timeout behavior during reboot or hotplug. Tests should cover unsupported capability bits, successful info parsing, configure/deconfigure accepted responses, queue timeout returning failed status, and memory allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_cmd.c -->
