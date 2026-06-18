# sources/distributed-fs/beegfs-go/ctl/internal/cmd/stats/server.go

Purpose: implements `beegfs stats server`, showing server request queue, worker, and throughput statistics for one or many metadata/storage nodes.

Important APIs/types/functions: `serverStats_Config`; `newServerStatsCmd`; `runServerstatsCmd`; `singleNode`; `multiNode`; `multiNodeAggregated`; `printData`.

Control flow: optional node argument selects history view for one node; omitting it prints latest rows for many nodes or aggregate history with `--sum`. `--sum` is rejected for a single node. The runner picks a collection function, creates a Printomatic with default/debug columns, collects and prints each interval, and formats raw or IEC unit values.

State and persistence: read-only. The only local state is loop timing and the configured history window. Backend returns server-side history for single/aggregate modes.

Dependencies and integration points: uses backend `ctl/pkg/ctl/stats`, BeeGFS entity parsing, unit conversion, Viper raw/debug flags, Cobra, and `cmdfmt`.

Risks: `History.Seconds()` truncates subsecond durations when slicing history. Timestamps greater than `math.MaxInt64` are printed raw. Continuous interval output defaults to one second. Multi-node rows are sorted by type then numeric ID.

Test signals: no direct tests. Useful tests would cover mode selection, `--sum` validation, history slicing, raw/unit formatting, sort order, and context cancellation.
