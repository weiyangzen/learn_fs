# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-dp/memory.json

Purpose: defines 69 DP memory-topic aliases, dominated by `OFFCORE_RESPONSE.*` combinations for request type versus DRAM/remote response classification, plus `MISALIGN_MEM_REF.STORE`.

Important APIs/types/functions: uses core event fields plus `MSRIndex` and `MSRValue` for offcore response programming. `jevents.py` maps `MSRIndex` `0x1a6,0x1a7` to the `offcore_rsp=` event attribute while `EventCode` `0xB7, 0xBB` identifies the offcore response events. Request families include `ANY_DATA`, `ANY_IFETCH`, `ANY_REQUEST`, `ANY_RFO`, `COREWB`, `DATA_IFETCH`, `DATA_IN`, `DEMAND_*`, `PF_*`, and `PREFETCH`.

Control flow: build-time generation converts each row into a perf alias with event select, umask, and offcore MSR filter bits. At runtime, selecting an alias causes perf to configure both the PMU event and the offcore response MSR filter.

State and persistence: the JSON is static. Runtime state consists of per-event PMU programming and offcore response MSR state held while perf events are active.

Dependencies and integration points: depends on `jevents.py` MSR handling, the x86 offcore PMU implementation, and mapfile selection for CPUID `GenuineIntel-6-2C`. Integrates with memory locality analysis, remote DRAM investigation, and cache-miss source attribution.

Risks: offcore response events are highly sensitive to correct MSR bitmasks. DP names use `ANY_DRAM_AND_REMOTE_FWD` and `OTHER_LOCAL_DRAM`; these differ from SP names such as `ANY_DRAM` and `LOCAL_DRAM`, so copying between models can break semantics. EventCode lists two selectors, but `JsonEvent` uses the first for event encoding unless the generator handles the pair as intended.

Test signals: `jq empty`, generated offcore aliases containing `offcore_rsp=`, `perf list offcore_response`, and hardware tests comparing mutually related filters such as demand data reads versus all data reads.
