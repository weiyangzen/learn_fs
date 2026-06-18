<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/stats_cli.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/stats_cli.rs

### Purpose
`stats_cli.rs` implements v1 I/O statistics commands for pools, nexus, replicas, plus a reset command. It provides formatted latency and byte counters.

### Important APIs, Types, And Functions
`StatsArgs` wraps `Pool`, `Nexus`, `Replica`, and `Reset`. `NameArgs` is an optional filter. `io_stats_row` formats a `v1rpc::stats::IoStats`, `adjust_bytes` converts bytes to binary units, and `ticks_to_time` converts SPDK ticks to microseconds using `tick_rate`.

### Control Flow
Each resource command calls the matching stats RPC with optional name, handles empty results with verbose messages, and prints a common table of operation counts, byte totals, average/aggregate latency ticks converted to time, and max/min latencies. Replica stats unwrap nested `stats` in each `ReplicaIoStats`. Reset sends `reset_io_stats(())` and prints completion.

### State, Persistence, And Dependencies
Read commands observe remote cumulative stats. Reset mutates remote counters. Dependencies include v1 stats protobufs, `byte_unit`, colored JSON, SNAFU, and shared context. It integrates with bdev/nexus/replica stats collection and SPDK tick-rate reporting.

### Risks And Test Signals
`ticks_to_time` divides by `tick_rate`; zero would panic. Replica nested stats are unwrapped. `adjust_bytes` always uses binary units and ignores global unit preference. Tests should cover zero tick rate, missing replica stats, empty named and unnamed results, reset behavior, JSON/default output, and latency conversion correctness.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/io-engine-client/v1/stats_cli.rs -->
