# sources/distributed-fs/moosefs/mfsmaster/chartsdata.c

`chartsdata.c` samples mfsmaster runtime metrics and feeds the common charts subsystem. It combines CPU, memory, filesystem operation counters, chunk operations, client traffic, chunkserver space, object counts, chunk health, server counts, and usage-difference data into the 70-slot chart schema.

`calcdefs`, `statdefs`, and `estatdefs` are initialized from `chartsdefs.h`. Cached globals `rss`, `virt`, `scpu`, and `ucpu` store resource usage. Public functions are `chartsdata_resusage` and `chartsdata_init`; internal registered hooks are `chartsdata_refresh`, `chartsdata_store`, and `chartsdata_term`.

`chartsdata_init` initializes CPU accounting, captures memory usage, registers a 60-second refresh, registers hourly chart storage, registers a destructor, and calls `charts_init` using `stats.mfs`. Each refresh fills all chart slots with `CHARTS_NODATA`, gathers subsystem metrics, sets `CHARTS_DELAY` to no data, and calls `charts_add(data, main_time()-60)`.

The charts subsystem persists samples to `stats.mfs`. Termination refreshes once, stores charts, and terminates chart state. Dependencies include `charts`, `main`, `chunks`, `filesystem`, `matoclserv`, `memusage`, `cpuusage`, `matocsserv`, `csdb`, and `chartsdefs`. `mfsstatsdump` shares the same definitions, so schema changes affect producer and consumer.

Risks are schema-index drift, CPU scaling assumptions, `CHARTS_DELAY` remaining unpopulated, and side effects or cost in subsystem stats calls. Test signals are successful `charts_init`, `stats.mfs` updates, non-no-data values under load, `mfsstatsdump` compatibility, and multi-interval refresh behavior.
