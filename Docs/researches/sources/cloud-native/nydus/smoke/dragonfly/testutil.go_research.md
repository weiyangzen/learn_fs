# sources/cloud-native/nydus/smoke/dragonfly/testutil.go

Purpose: shared process, nydusd, Dragonfly cluster, port, mount, cache, log, and filesystem traversal utilities for Dragonfly smoke tests.

Important APIs/types: `Process`, `StartProcess`, `Stop`, `Restart`, `NydusdInstance`, `StartNydusd`, `NydusdInstance::{Stop,Restart,LogLineCount,LogSince,LogContains}`, `DragonflyEnv`, `SetupDragonflyCluster`, `Teardown`, `WaitForPort`, `WaitForPortClosed`, `WaitForMount`, `ClearCaches`, `ParseCacheDir`, `CountFiles`, `FindFiles`, and `WaitForLogPattern`.

Control flow: `StartProcess` opens a log, starts a process in a new process group, writes a pid file, and waits for an optional TCP port. `Stop` sends SIGTERM, waits with timeout, kills if needed, then waits for port closure. `StartNydusd` builds standard CLI args, starts nydusd, and waits for the mountpoint. Cluster setup starts manager, scheduler, and dfdaemon on fixed ports from env configs. Utility waits poll ports, mountpoint command, log patterns, or filesystem traversal.

State and persistence: creates log/stdout/pid files, tracks process handles, reuses/suffixes logs on restart, mutates mount and cache directories, and writes `/proc/sys/vm/drop_caches`.

Dependencies and integration: depends on external binaries (`manager`, `scheduler`, `dfdaemon`, `nydusd`, `umount`, `mountpoint`), root permissions for cache dropping and unmounts, JSON config schema for blob cache work dir, and `testify/require`.

Risks: fixed ports can collide, scanner defaults may truncate very long log lines, stop does not signal whole process group despite setting pgid, cache clearing removes all entries under supplied dirs, and dropping kernel caches requires privileges. `FindFiles` returns `SkipDir` for too-deep files, which can behave unexpectedly when the current entry is not a directory.

Test signals: helpers fail fast when ports/mounts do not become ready or close, config parsing lacks `work_dir`, or process startup fails; higher-level tests use log line deltas and pattern detection for proxy health behavior.
