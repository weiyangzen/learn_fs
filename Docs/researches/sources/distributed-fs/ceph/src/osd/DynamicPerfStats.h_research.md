# sources/distributed-fs/ceph/src/osd/DynamicPerfStats.h

## Purpose
`DynamicPerfStats.h` implements dynamic OSD performance metric aggregation for manager-defined queries. It tracks counters per `OSDPerfMetricQuery` and key, updates them from OSD operations, merges reports, and emits bounded reports with optional sampling.

## Important APIs, Types, and Control Flow
Constructors initialize `data` from query lists. `merge()` adds counters from another instance by replaying query descriptors. `set_queries()` preserves matching existing counters while dropping disabled queries. `is_enabled()` checks if any query is active. The templated `add()` derives counter increments from op capabilities (`may_write`, `may_cache`, `may_read`), in/out bytes, latency, and query subkeys such as client id, client address, pool id, namespace, OSD id, PG id, object name, and snap id. `add_to_reports()` packs counters into `OSDPerfMetricReport` structures, either all groups or sampled groups when limits apply.

## State and Persistence Behavior
State is in-memory: a nested map from query to metric key to `PerformanceCounters`. There is no durable persistence. Report generation packs counters into bufferlists for manager reporting. Limited reports use weighted random sampling (A-Chao style) based on the chosen counter descriptor.

## Dependencies and Integration Points
It depends on random utilities, stringification, `MOSDOp`, and manager OSD perf metric types. It integrates with OSD op accounting and mgr perf query/report pathways, including Crimson and classic connection address handling.

## Risks and Test Signals
Risks include query descriptor mismatch during merge, regex subkey extraction failures, unsupported counter/subkey types aborting, random sampling bias, and limits ordered by a descriptor not present in the query. Tests should cover each counter type, each subkey type, query reconfiguration preserving counters, merge with multiple keys, report packing with and without limits, and deterministic sampling by controlled random seeds where possible.
