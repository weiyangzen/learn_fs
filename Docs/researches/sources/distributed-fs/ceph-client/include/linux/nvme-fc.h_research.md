
# sources/distributed-fs/ceph-client/include/linux/nvme-fc.h

Purpose: defines FC-NVMe wire-format constants and structures for command IUs, response IUs, status/readiness IUs, link-service descriptors, link-service payloads, timeouts, and transport address formatting.

Important APIs/types/functions: command flags encode read/write and protection information. `fccmnd_set_cat_admin()` and `fccmnd_set_cat_css()` set command category bits. `struct nvme_fc_cmd_iu`, `nvme_fc_ersp_iu`, `nvme_fc_nvme_sr_iu`, and `nvme_fc_nvme_sr_rsp_iu` model FCP command/response/readiness exchanges. Link-service enums and descriptors model create association, create connection, disconnect association/connection, accept, reject, association ID, and connection ID. TRADDR macros define FC address string lengths and offsets.

Control flow: host and target code build link-service requests to create associations/connections, accept or reject them using descriptor lists, exchange NVMe command IUs and response IUs over FC sequences, and use disconnect LS payloads for teardown. Helpers fill length/category fields according to FC-NVMe layout rules.

State and persistence: no software state is owned here. Structures represent on-wire transient protocol payloads; association and connection IDs persist only for the lifetime of the FC-NVMe session.

Dependencies and integration points: depends on FC UAPI constants from `fc_fs.h`, NVMe command/completion structures, endian types, UUIDs, and offset calculations. It integrates `nvme-fc-driver.h`, NVMe host/target transports, and FC LLDD payload parsing.

Risks and test signals: risks include endian mistakes, descriptor length miscalculation, accepting malformed descriptor lists, TRADDR parsing inconsistencies with required `0x` prefixes, and mismatched association/connection IDs. Test signals include protocol conformance tests for LS payload sizes, create/disconnect association flows, invalid reject reason/explanation handling, FC-NVMe interop, and fuzzing of LS descriptor lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nvme-fc.h -->
