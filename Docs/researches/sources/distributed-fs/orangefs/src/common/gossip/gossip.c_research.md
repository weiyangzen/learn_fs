# sources/distributed-fs/orangefs/src/common/gossip/gossip.c

Purpose: Implements the OrangeFS `gossip` logging interface for debug and error output to stderr, files, or syslog.

Important APIs/functions: `gossip_enable_stderr()`, `gossip_enable_file()`, `gossip_enable_syslog()`, `gossip_reopen_file()`, and `gossip_disable()` switch facilities while preserving debug mask state. `gossip_set_debug_mask()`/`gossip_get_debug_mask()` control global debug enablement and bitmask. `__gossip_debug()`/`__gossip_debug_va()` route debug messages after macro-level filtering. `gossip_err()` logs unmasked errors. `gossip_debug_fp_va()` formats prefixes and timestamps; syslog helpers wrap `syslog()`. Optional `gossip_backtrace()` emits stack traces and exits after repeated backtraces.

Control flow: Facility enablement first disables the current facility, then activates the new sink and restores debug flags. Debug calls are filtered by macros on GCC builds, normalized to prefix `D` if `?`, then dispatched by `gossip_facility`. File/stderr messages are buffered into `GOSSIP_BUF_SIZE`, timestamped, written, and flushed.

State/persistence: Global mutable state includes `gossip_debug_on`, `gossip_debug_mask`, `gossip_facility`, `internal_log_file`, syslog priority, and timestamp mode. File logging persists to the configured filename.

Dependencies/integration: Uses `gen-locks.h` only for thread-stamp IDs, syslog on POSIX, `wincommon.h` on Windows, and optional execinfo. `gossip.h` provides macros used broadly by OrangeFS.

Risks: Global state is not protected by locks, so concurrent facility changes/logging can race. File logging flushes every line, impacting performance. Timestamp formatting uses `localtime()` which is not thread-safe on many platforms. Windows syslog functions are stubs.

Test signals: Verify all facilities, timestamp modes, mask filtering, reopen behavior, disabled facility behavior, long messages/truncation, and optional backtrace builds.
