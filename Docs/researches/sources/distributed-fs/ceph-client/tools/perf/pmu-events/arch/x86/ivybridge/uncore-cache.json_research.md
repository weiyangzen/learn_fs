# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivybridge/uncore-cache.json

Purpose: Defines 25 Ivy Bridge uncore C-box cache/coherency aliases for LLC lookup state and cross-snoop response accounting. These names let perf users request package-level CBOX events without spelling raw uncore event encodings.

Important APIs/types/functions: Every entry is a PMU event object using `EventName`, `EventCode`, `UMask`, `Unit`, `Counter`, `PerPkg`, and `BriefDescription`. The file has two families: `UNC_CBO_CACHE_LOOKUP` with 16 variants covering request classes (`ANY`, `EXTSNP`, `READ`, `WRITE`) crossed with MESI hit states, and `UNC_CBO_XSNP_RESPONSE` with 9 variants covering snoop sources (`EVICTION`, `EXTERNAL`, `XCORE`) and responses (`MISS`, `HIT`, `HITM`). `Unit: CBOX` directs perf to uncore C-box PMUs, and `PerPkg: 1` marks package-level aggregation.

Control flow: Perf's generated event table maps these aliases into uncore PMU configurations. Runtime lookup selects Ivy Bridge by CPU model, resolves an alias such as `UNC_CBO_CACHE_LOOKUP.READ_MESI`, chooses the CBOX unit, applies event select and unit mask, and schedules the event on available CBOX counters. Counts are package/unit scoped rather than per-thread core PMU counts.

State and persistence: Static JSON preserves Intel uncore event encodings. There is no mutable state in the file. Hardware CBOX counters hold runtime state, and perf records or aggregates the resulting counts.

Dependencies/integration: Depends on the kernel exposing Ivy Bridge CBOX uncore PMUs with names understood by perf. Integrates with uncore interconnect events and with derived memory/coherency analysis outside this file. Its event names are not regular core aliases; consumers must respect the `Unit` and `PerPkg` fields.

Risks: Uncore topology varies by socket and SKU, so event availability and aggregation can differ across systems. `PerPkg` counts can be misread as per-core if UI layers drop unit context. MESI and snoop-response masks are dense; transposed `UMask` values would silently count a different cache state. Counter availability is limited to CBOX counters `0,1`, so broad event groups may multiplex.

Test signals: Run JSON validation, perf alias lookup for at least one lookup and one xsnp response event, and on-Ivy-Bridge hardware `perf stat -e uncore_cbox_*/event=.../` equivalence checks where possible. Tests should verify `Unit` remains `CBOX`, `PerPkg` remains set, and generated tables keep package scoping.
