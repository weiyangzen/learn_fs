# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/other.json

Purpose: groups 23 miscellaneous SP events for load dispatch, store-buffer stalls, segment rename activity, I/O transactions, snoop queue requests/outstanding cycles, snoop responses, and super-queue full stalls.

Important APIs/types/functions: the schema is standard PMU event JSON with `CounterMask` on not-empty cycle aliases. Families include `LOAD_BLOCK.OVERLAP_STORE`, `LOAD_DISPATCH.*`, `SNOOPQ_REQUESTS.*`, `SNOOPQ_REQUESTS_OUTSTANDING.*`, `SNOOP_RESPONSE.*`, `SB_DRAIN.ANY`, and `SQ_FULL_STALL_CYCLES`.

Control flow: records are parsed by `jevents.py`, topic-tagged from `other.json`, emitted into generated C, and exposed at runtime through perf's event alias lookup for the `westmereep-sp` table.

State and persistence: static descriptor data only. Runtime state is active PMU event configuration.

Dependencies and integration points: complements SP cache and memory topics for coherence and load/store behavior. Snoop-related entries are useful when interpreting multi-core sharing even on the single-processor Westmere-EP model family.

Risks: miscellaneous grouping makes discoverability and semantic consistency weaker than topic-specific files. Counter-mask rows such as `*_NOT_EMPTY` represent cycles meeting a condition, while similarly named rows without that suffix count outstanding requests. Some rows use only counter `0`, causing grouping constraints.

Test signals: `jq empty`, generated aliases in `perf list`, stress tests for store forwarding/partial address aliasing, and coherence-heavy workloads for snoop response events.
