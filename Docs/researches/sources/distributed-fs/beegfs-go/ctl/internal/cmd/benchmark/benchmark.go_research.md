# sources/distributed-fs/beegfs-go/ctl/internal/cmd/benchmark/benchmark.go

Purpose: implements the `beegfs benchmark` command family for starting, stopping, cleaning up, watching, waiting for, and reporting storage target benchmarks.

Important APIs/types are `frontendCfg`, `NewBenchmarkCmd`, subcommand builders, `storageBenchDispatcher`, `hasActiveBenchmark`, `hasBenchmarkError`, `refreshScreenAndPrintResults`, output table functions, `normalizeStorageBenchResults`, `benchStatusResults`, and `benchPerfResults`.

Control flow: the root command defines node/target filters, wait/watch refresh interval, unadorned table mode, and verbose output. Subcommands set `benchmark.StorageBenchConfig.Action` and related backend fields, then call `storageBenchDispatcher`. The dispatcher executes backend action once, optionally switches to status polling for wait/watch, refreshes terminal output, stops when no active benchmark remains, and emits a terminal alert. Status printing renders overall status, optional per-node errors/debug details, summary metrics, and verbose target rows.

State is split between frontend display options and backend benchmark config. Backend execution occurs through `ctl/pkg/ctl/benchmark.ExecuteStorageBenchAction`; this file does not persist benchmark files itself but commands can cause storage nodes to create/delete benchmark data.

Dependencies include cobra/pflag/viper, go-pretty tables/text, unit conversion, BeeGFS benchmark enums/entities, CTL config flags, terminal utilities, and backend benchmark package.

Integration points are storage node benchmark RPCs/ioctls via backend package, terminal refresh, global raw/debug config, and entity ID pflags.

Risks: parent flag sets are added to multiple subcommands, which must remain compatible with cobra behavior. Status without filters can aggregate unrelated benchmark runs and warns users. Mixed read/write results refuse summary. Throughput conversion assumes backend values are KiB/s. Wait/watch with zero interval can create an invalid ticker if validation is not elsewhere enforced.

Test signals: `benchmark_test.go` covers performance summary aggregation. Command dispatch and terminal rendering are otherwise untested.
