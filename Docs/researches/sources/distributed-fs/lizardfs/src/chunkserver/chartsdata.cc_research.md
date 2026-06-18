# sources/distributed-fs/lizardfs/src/chunkserver/chartsdata.cc

## Purpose
`chartsdata.cc` periodically collects chunkserver runtime counters and feeds the shared LizardFS chart storage engine, persisting data to `csstats.mfs`.

## Important APIs, Types, And Functions
- `CHARTS_*` constants define 30 raw chart slots: CPU, master traffic, chunkserver network traffic, HDD overhead/total I/O, high-level ops, read/write time, replication, chunk operations, tests, and queue depths.
- `STATDEFS` defines chart names, join modes, percentage flags, scale, multipliers, and divisors for raw charts.
- `ESTATDEFS` defines derived aggregate charts such as CPU, data traffic, total bytes with overhead, low-level ops with overhead, and job totals.
- `chartsdata_refresh` gathers one sample and calls `charts_add`.
- `chartsdata_store` persists chart state.
- `chartsdata_term` refreshes, stores, and terminates the chart subsystem.
- `chartsdata_init` initializes CPU timers, registers event-loop refresh/store/destructor callbacks, and calls `charts_init`.

## Control Flow
Initialization arms virtual/profiling timers with large countdown values, registers a 60-second refresh and an hourly store, then initializes charts. Each refresh computes elapsed user and system CPU from timer deltas, gathers master connection stats, network stats, HDD stats, legacy and modern replication counts, and HDD operation counts. The sample is timestamped as `eventloop_time() - 60`, matching the just-finished interval.

## State And Persistence
Chart state is maintained by the shared `common/charts` module and persisted in `csstats.mfs`. CPU accounting state is held in process timers `ITIMER_VIRTUAL` and `ITIMER_PROF`. Replication count from `gReplicator.getStats()` is reset when sampled.

## Dependencies And Integration Points
This file integrates with `masterconn_stats`, `networkStats`, `hdd_stats`, `legacy_replicator_stats`, `gReplicator.getStats`, `hdd_op_stats`, `eventloop_timeregister`, `eventloop_destructregister`, and `common/charts`.

## Risks
- CPU accounting uses process interval timers and includes comments noting Linux timer oddities; incorrect timer behavior can distort CPU charts.
- The modern replication stat is reset during sampling, so skipped refreshes can change observed granularity.
- New chart ids must stay aligned with the CGI chart names and `chart.cgi` expectations.
- `chartsdata_term` performs a final refresh, which can double count if shutdown occurs close to a scheduled refresh.

## Test Signals
No direct unit tests are listed. Existing signals are integration-oriented: chart files should be created/stored and the CGI chart views reference ids matching this chart definition table.
