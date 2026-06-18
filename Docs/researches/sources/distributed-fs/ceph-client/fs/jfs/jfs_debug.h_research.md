# sources/distributed-fs/ceph-client/fs/jfs/jfs_debug.h

## Purpose
Centralizes JFS assert, logging, procfs, and statistics macros behind config options.

## Important APIs, types, and functions
Defines `PROC_FS_JFS`, always-on `assert()`, debug-only `ASSERT()`, loglevel constants, `jfs_info/debug/warn/err()`, statistics show prototypes, and statistic mutation macros.

## Control flow
Source files call macros unconditionally; the preprocessor compiles real logging/stat updates or erases them depending on config.

## State and persistence behavior
No persistent state. Runtime logging depends on global `jfsloglevel`; statistics live in owning modules.

## Dependencies and integration points
Integrates with printk, BUG assertions, procfs declarations, seq_file show functions, and JFS diagnostics.

## Risks and test signals
Watch for side effects in compiled-out macro arguments and assertion panics. Build debug/statistics on/off and validate loglevel gating under workload.
