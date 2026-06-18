# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dump.c

## Purpose
Provides diagnostic dump support for dm-vdo. It implements the `dump` dmsetup message path and shutdown dump helper, logging work queues, hash-zone/index state, data_vio pool state, VDO status, and memory usage. It also implements the data_vio pool item dumper used by the pool dump.

## Important APIs, Types, And Functions
Public functions are `vdo_dump()`, `vdo_dump_all()`, and `dump_data_vio()`. Internally, `enum dump_options` and `enum dump_option_flags` define selectable categories: queues/threads, VIO pool, and VDO status. `DEFAULT_DUMP_FLAGS` includes queues and VDO status, while options such as `viopool`, `pools`, `queues`, `threads`, `vdo`, `default`, and `all` control the exact output.

`parse_dump_options()` accepts case-insensitive option prefixes via `is_arg_string()`, accumulates flags, rejects unknown option names, and applies defaults unless an explicit option set requested `FLAG_SKIP_DEFAULT`. `do_dump()` emits the high-level dump and calls subsystem dump functions. `dump_vio_waiters()`, `encode_vio_dump_flags()`, and `dump_data_vio()` produce compact per-data_vio log lines.

## Control Flow
`dm-vdo-target.c` routes a `dmsetup message ... dump [options...]` to `vdo_dump()`. After parsing, `do_dump()` logs the trigger reason, active/max data_vio pool usage, outstanding bio count, and device name. If queue output is enabled and threads exist, each VDO work queue is dumped. Hash zones are always dumped. The data_vio pool is dumped with or without detailed pool contents depending on `FLAG_SHOW_VIO_POOL`. VDO status and memory usage are then logged.

`vdo_dump_all()` bypasses parsing and passes all flags, used for shutdown when `dump-on-shutdown` has been requested. `dump_data_vio()` is invoked as a callback from the data_vio pool dumper and logs block numbers, flush generation, current operation, completion location, compact flags, and logical-block waiters.

## State And Persistence
This file does not mutate persistent VDO state. It reads volatile runtime state: pool active counts, bio counters, thread queues, hash-zone state, data_vio fields, wait queues, and memory usage. Several dump buffers in `dump_data_vio()` are static to avoid repeated allocations during heavy logging; the code assumes only one dump runs at a time and notes that concurrent dumps would garble logs.

## Dependencies And Integration Points
It depends on VDO logging, memory accounting, string helpers, constants, data_vio, dedupe, funnel work queues, I/O submitter, types, and VDO status helpers. It integrates with the DM message handler in `dm-vdo-target.c`, `vdo_dump_hash_zones()` in dedupe, `dump_data_vio_pool()` in the data_vio pool, work queue dump support, and `vdo_report_memory_usage()`.

## Risks
Diagnostic code must avoid making a stressed system worse. `all` or VIO pool dumps can log thousands of lines, so output volume can overwhelm logs during a failure. Prefix matching means abbreviated options are accepted, but ambiguous future option names could change behavior. Static buffers are intentionally not concurrency-safe. The function always dumps hash zones regardless of option flags, so callers requesting narrow output still receive index/hash diagnostics.

## Test Signals
Exercise `dmsetup message <dev> 0 dump`, `dump all`, `dump queues`, `dump viopool`, unknown options, and `dump-on-shutdown`. Check that default output includes queues/status, unknown options return `-EINVAL`, active/outstanding counts are plausible, data_vio lines are bounded and non-overlapping under single dump, and no dump path sleeps or allocates in unsafe contexts.
