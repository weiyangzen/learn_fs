# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/meteorlake/uncore-interconnect.json

Purpose: defines seven Meteor Lake uncore interconnect and arbitration events. The catalog covers read data occupancy, coherent tracker allocation, outgoing coherent data-read requests, CMI transaction totals, CMI reads, CMI writes, and all outgoing HAC ARB tracker allocations.

Important APIs/types/functions: static event rows with `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and descriptions. Units are `ARB` for `UNC_ARB_DAT_OCCUPANCY.RD` and `HAC_ARB` for the remaining coherent tracker and transaction events. Event codes include `0x85`, `0x84`, `0x81`, and `0x8A`; counters are constrained to `0` or `0,1` depending on the PMU.

Control flow: perf's build generator reads the JSON and emits C aliases. A user selecting one of these names causes perf to address the relevant uncore arbitration PMU and program the encoded event. Occupancy events are cycle-weighted, while request and transaction events count allocations or CMI transfers.

State and persistence: static source data only. Runtime state is in uncore counters, package-level because `PerPkg` is set on all entries. The data is not persisted by this file; perf may persist samples or aggregate counts.

Dependencies and integration points: depends on Meteor Lake uncore PMU support and generated `pmu-events` tables. It integrates with uncore cache events for queue pressure and uncore memory events for downstream DRAM traffic, allowing read occupancy and transaction counts to be correlated.

Risks: event descriptions distinguish coherent versus non-coherent traffic and reads versus writes; alias misuse can produce misleading bandwidth or occupancy interpretations. The single-counter `ARB` occupancy event may fail scheduling if combined with other events requiring the same counter. Counter constraints and `Unit` values must match kernel-exposed PMU names.

Test signals: `jq` schema validation, generated table checks, `perf list` visibility, and `perf stat` runs under read-heavy and write-heavy workloads. A useful behavioral signal is that `UNC_HAC_ARB_TRANSACTIONS.READS` and `.WRITES` should move differently under synthetic traffic while `.ALL` remains a superset.
