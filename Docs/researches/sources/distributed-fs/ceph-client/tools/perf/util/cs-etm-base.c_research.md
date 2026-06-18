# sources/distributed-fs/ceph-client/tools/perf/util/cs-etm-base.c

Purpose: handles OpenCSD-independent CoreSight ETM auxtrace metadata validation and optional dump printing before delegating full processing.

Important APIs/functions: exports `cs_etm__process_auxtrace_info`; internal metadata printers handle v0 and v1/v2 ETMv3, ETMv4, and ETE layouts.

Control flow: verifies record size, reads the u64 private header, rejects unsupported header versions, optionally prints metadata when `dump_trace` is set, and calls `cs_etm__process_auxtrace_info_full`.

State and persistence: no mutable state beyond stdout dump output; consumes metadata in memory.

Dependencies and integration: `cs-etm.h` constants, perf auxtrace event layout, session type, `dump_trace`, and the full ETM processor.

Risks: metadata printing indexes based on header counts and assumes size validation is sufficient. Unknown future params are generic only for supported layouts. Dump output goes directly to stdout.

Test signals: ETMv3/ETMv4/ETE records, header versions 0/1/2, bad magic, too-small records, future version, dump on/off, and full delegation.
