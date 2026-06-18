# sources/distributed-fs/moosefs/mfschunkserver/chartsdata.c

## Purpose
`chartsdata.c` is the chunkserver metrics collection bridge. It periodically samples CPU, memory, master traffic, client service traffic, disk I/O, replication, chunk operations, space usage, disk health, and chunk layout counters, then writes those samples into the common MooseFS charts subsystem.

## Important Functions
`chartsdata_refresh` fills a `uint64_t data[CHARTS]` array initialized to `CHARTS_NODATA`. It samples CPU with `cpu_used`, memory with `mem_used`, master traffic with `masterconn_stats`, background load with `job_stats`, service traffic with `csserv_stats` and `mainserv_stats`, disk metrics with `hdd_stats`, replication with `replicator_stats`, operation counts with `hdd_op_stats`, space with `hdd_get_space`, and disk/chart detail with `hdd_get_chart_data`. It then calls `charts_add(data, main_time() - 60)`.

`chartsdata_store` calls `charts_store`. `chartsdata_term` forces one final refresh, stores chart data, and terminates the charts subsystem. `chartsdata_init` initializes CPU tracking, registers refresh every 60 seconds, store every 3600 seconds offset by 30 seconds, registers destruct handling, and calls `charts_init` with `CALCDEFS`, `STATDEFS`, `ESTATDEFS`, and `CHARTS_FILENAME`.

## Control Flow
The module is passive after initialization. The common main loop invokes registered time callbacks. Each refresh consumes delta-style counters from contributing modules; several stats functions reset their counters after returning, so refresh cadence controls aggregation windows. The timestamp uses `main_time() - 60`, indicating the sample represents the preceding minute.

## State and Persistence
Persistent chart data is managed by `charts.c` using `CHARTS_FILENAME` (`csstats.mfs`) from `chartsdefs.h`. This file itself holds only static definitions generated from macros. Termination explicitly stores data to reduce loss on shutdown.

## Dependencies and Integration
This module integrates almost every chunkserver subsystem that exposes counters: `bgjobs`, `csserv`, `mainserv`, `masterconn`, `hddspacemgr`, and `replicator`. It also depends on common `charts`, `main`, `cpuusage`, and `memusage`. The numeric indexes in `chartsdefs.h` must match the positions filled here.

## Risks
Metric ordering is brittle: a mismatch between `CHARTS_*` indexes and `STATDEFS` corrupts chart meaning. Counter reset semantics mean accidental double refresh or missing refresh changes observed rates. Some fields are added together, such as `CHARTS_CSSERVIN/OUT` including both `csserv` and `mainserv` bytes; changing one source can affect historical interpretation. `data[CHARTS_CHANGE]` is derived from several operation counters and must be updated when chunk-changing operations expand.

## Test Signals
Signals include successful `chartsdata_init`, creation/loading of `csstats.mfs`, periodic samples with non-`CHARTS_NODATA` values after simulated activity, final store on destruct, and stats dump compatibility through `mfscsstatsdump`. Unit-style tests can stub provider stats and assert exact `CHARTS_*` array positions.
