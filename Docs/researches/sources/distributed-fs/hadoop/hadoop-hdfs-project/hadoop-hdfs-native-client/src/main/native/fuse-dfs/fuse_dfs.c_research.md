# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/fuse_dfs.c

## Purpose
Main executable entry for the HDFS FUSE client. It parses mount options, registers FUSE callbacks, and starts `fuse_main`.

## Important APIs, Types, And Functions
`is_protected()` checks mount-protected paths from `dfs_context`. `dfs_oper` maps FUSE operations to `dfs_*` implementations. `main()` initializes defaults, parses `dfs_opts`, translates options to FUSE arguments, and invokes `fuse_main`.

## Control Flow
Process startup clears umask, initializes global `options`, parses command-line and mount options, adds `allow_other` unless private, adds default permission enforcement unless disabled, translates read-only mode and cache timeouts to FUSE args, requires a NameNode URI, then enters FUSE. libhdfs initialization is intentionally deferred to `dfs_init` after FUSE daemonization/fork.

## State, Persistence, And Dependencies
Global `options` persists through startup and mount initialization. FUSE owns callback lifecycle after `fuse_main`. Protected path checks depend on the mount context created later.

## Integration Points
This file binds all operation modules, option parsing, initialization, and connection management into the runnable `fuse_dfs` binary.

## Risks
Option parsing is order-sensitive for URI/server handling. FUSE args are constructed manually. `is_protected` only checks exact paths, not descendants. Read-only behavior is delegated to kernel FUSE rather than operation checks.

## Test Signals
Successful mount, option translation (`ro`, `allow_other`, `default_permissions`, timeout settings), and correct callback dispatch are the primary signals.
