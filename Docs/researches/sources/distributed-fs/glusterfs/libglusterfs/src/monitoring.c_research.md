# sources/distributed-fs/glusterfs/libglusterfs/src/monitoring.c

## Purpose
`monitoring.c` writes a point-in-time Gluster metrics snapshot to a temporary file, typically triggered by a monitoring request such as SIGUSR2. It emits process metadata, stack and dictionary counters, per-translator FOP counts/latencies, memory accounting details, and translator-specific custom metrics.

## Important APIs, Types, And Functions
The public entry point is `char *gf_monitor_metrics(glusterfs_ctx_t *ctx)`, declared in `glusterfs/monitoring.h`. Internal helpers include `dump_mem_acct_details()`, `dump_latency_and_count()`, `dump_call_stack_details()`, `dump_dict_details()`, `dump_inode_stats()` (currently empty), `dump_global_metrics()`, and `dump_xl_metrics()`.

## Control Flow
`gf_monitor_metrics()` chooses `ctx->config.metrics_dumppath` or `GLUSTER_METRICS_DIR`, creates the directory, allocates a `gmetrics.XXXXXX` template, opens it with `mkstemp()`, writes global metrics, walks translator metrics, writes an end marker, fsyncs, closes, and returns the allocated filepath for the caller to consume. `dump_xl_metrics()` starts at `ctx->active->top`, walks `xl->next`, and also handles `ctx->root`.

`dump_latency_and_count()` emits pending winds, skips inactive old graph translators except the root, loops over `GF_FOP_MAXVALUE`, reads total counts, atomically swaps interval counts/fail counts to zero, writes average/max/min latency for nonzero latency samples, and clears each latency struct with `memset()`.

## State And Persistence
The module persists one metrics file per call in the metrics directory and returns ownership of the path string to the caller. It destructively resets interval FOP counters, interval callback counts, and latency accumulators after dumping. Total counters are read but not reset. Memory accounting and stack/dict stats are read from live context structures.

## Dependencies And Integration Points
Dependencies include `glusterfs/monitoring.h`, `xlator.h`, `syscall.h`, `mkdir_p()`, `gf_asprintf()`, `gf_time()`, `gf_fop_list`, atomic counters, memory accounting records, call stack pool state, dict stats, latency structs from `latency.c`, and optional `xl->dump_metrics()` callbacks.

## Risks
`dump_dict_details()` divides `total_pairs / total_dicts` without guarding `total_dicts == 0`. `dump_latency_and_count()` resets latency with plain `memset()` rather than `gf_latency_reset()`, so `min` becomes zero until new samples arrive. Metrics dumping is not globally synchronized with live FOP updates; interval counters use atomic swaps, but latency fields are non-atomic. Returned `filepath` can leak if the caller does not free it. The log message IDs used for mkdir/open/fsync errors are generic string-dup IDs rather than monitoring-specific IDs.

## Test Signals
Tests should call `gf_monitor_metrics()` with default and configured directories, verify file creation and permissions, assert interval counters reset after dump, check latency output and post-reset behavior, exercise no-dict zero-count cases, validate active graph filtering, and verify translator `dump_metrics()` callbacks are invoked. Fault injection for mkdir, mkstemp, dprintf, and fsync should be included.
