# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_options.c

## Purpose
Command-line and mount-option parser for `fuse_dfs`.

## Important APIs, Types, And Functions
Defines `program`, `dfs_opts`, option keys, `print_options`, `print_usage`, and `dfs_options`. Recognized options include server/port/protected/cache timeouts/read buffer/max background/private/ro/rw/debug/initchecks/nopermissions/big_writes/usetrash/notrash/direct_io.

## Control Flow
`fuse_opt_parse` uses `dfs_opts` and calls `dfs_options` for special keys. Version/help print and exit. Debug adds `-d` to FUSE args. `big_writes` forwards to FUSE when supported. Unknown non-URI options are passed through to FUSE. URI arguments set `options.nn_uri`, translating legacy `dfs://` to `hdfs://`.

## State, Persistence, And Dependencies
Mutates the global `options` struct declared in the header and the outgoing FUSE arg list. Depends on libfuse option parsing and C allocation for URI translation.

## Integration Points
Called from `main` before `fuse_main`; its parsed state is consumed by `dfs_init`, `fuse_dfs.c`, and operation callbacks.

## Risks
The usage string contains typos and stale option spelling. URI memory is allocated and never freed. Unknown options are mostly passed through, which can hide misspellings. Multiple URI/server options are ignored after first.

## Test Signals
Mounts with URI, server/port, ro/rw, debug, cache timeout, and legacy `dfs://` forms validate this parser.
