# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/westmereep-sp/memory.json

Purpose: defines 67 SP offcore-response memory aliases focused on request type versus DRAM locality. Unlike the SP cache file, this topic is a narrower memory classification set.

Important APIs/types/functions: all rows are `OFFCORE_RESPONSE.*` entries with `EventCode` `0xB7, 0xBB`, `UMask` `0x1`, generic counters, and `MSRIndex`/`MSRValue` offcore filters. Request families include `ANY_DATA`, `ANY_IFETCH`, `ANY_REQUEST`, `ANY_RFO`, `COREWB`, `DATA_IFETCH`, `DATA_IN`, `DEMAND_*`, `PF_*`, and `PREFETCH`. Response suffixes include `ANY_DRAM`, `LOCAL_DRAM`, `REMOTE_DRAM`, and for most families `ANY_LLC_MISS`.

Control flow: `jevents.py` maps the MSR index to `offcore_rsp=` while generating C table entries. Runtime perf configures the offcore response event and the associated MSR value for each selected alias.

State and persistence: source data is static. Runtime state is temporary PMU and offcore MSR programming.

Dependencies and integration points: integrates with memory locality analysis and overlaps semantically with many `OFFCORE_RESPONSE.*` rows in `cache.json`. It is selected via the `westmereep-sp` mapfile directory.

Risks: this SP memory table differs from DP: it lacks `MISALIGN_MEM_REF.STORE`, uses `LOCAL_DRAM` instead of `OTHER_LOCAL_DRAM`, and uses `ANY_DRAM` instead of `ANY_DRAM_AND_REMOTE_FWD`. Duplicate-looking aliases across `cache.json` and `memory.json` can confuse users if both topics expose similar names.

Test signals: valid JSON, generated offcore aliases, `perf list offcore_response`, and hardware memory placement tests that distinguish local and remote DRAM.
