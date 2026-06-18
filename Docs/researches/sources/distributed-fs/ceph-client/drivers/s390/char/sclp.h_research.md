<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp.h

**Purpose:** `sclp.h` is the shared SCLP internal ABI for s390 character and platform code. It defines event types, command words, SCCB layouts, request and registration structures, early-console hooks, and helper functions for masks and GDS parsing.

**Important APIs and types:** Key structures are `init_sccb`, `read_cpu_info_sccb`, `read_info_sccb`, `read_storage_sccb`, `sclp_req`, and `sclp_register`. Macros define event masks such as `EVTYP_MSG_MASK`, `EVTYP_DIAG_TEST_MASK`, `EVTYP_STORE_DATA_MASK`, and command words such as `SCLP_CMDW_READ_SCP_INFO`, `SCLP_CMDW_WRITE_EVENT_DATA`, and `SCLP_CMDW_WRITE_EVENT_MASK`. Inline helpers read/write variable-length event masks, issue `sclp_service_call()`, translate ASCII/EBCDIC by environment, and find GDS vectors/subvectors.

**Control flow, state, and persistence:** `struct sclp_req` is the persistent request object while queued/running and carries status, callback, SCCB pointer, and timeout fields. `struct sclp_register` is the persistent event registration object used to compute send/receive masks and dispatch inbound events.

**Dependencies and integration:** It depends on Linux list/types and s390 machine, SCLP, EBCDIC, and assembly exception-table definitions. The global `sclp` capability object is populated by early SCLP discovery.

**Risks and test signals:** Risks are layout drift from hardware SCCB specs, endian/packing mistakes, mask-length compatibility issues, and unvalidated GDS vector lengths in callers. Tests should validate service-call condition-code mapping, mask helpers with 4-byte and 8-byte masks, CPU/storage info parsing, and GDS traversal with malformed lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp.h -->
