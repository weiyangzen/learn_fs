# sources/distributed-fs/glusterfs/libglusterfs/src/logging.c

## Purpose
`logging.c` implements GlusterFS' core logging infrastructure: global context defaults, log file initialization and rotation, syslog integration, message formatting with IDs, duplicate suppression buffers, no-memory logging paths, command-history logging, structured message formatting, backtraces, and shutdown cleanup.

## Important APIs, Types, And Functions
The public surface is declared in `glusterfs/logging.h`. Initialization and configuration APIs include `gf_log_globals_init()`, `gf_log_init()`, `gf_log_fini()`, `gf_log_enable_syslog()`, `gf_log_disable_syslog()`, `gf_log_set_loglevel()`, `gf_log_set_xl_loglevel()`, `gf_log_set_localtime()`, `gf_log_set_logformat()`, `gf_log_set_logger()`, `gf_log_set_log_buf_size()`, `gf_log_set_log_flush_timeout()`, `gf_log_inject_timer_event()`, and `set_sys_log_level()`. Runtime logging APIs are macro-backed internal functions: `_gf_msg()`, `_gf_msg_plain()`, `_gf_msg_plain_nomem()`, `_gf_msg_nomem()`, `_gf_log()`, `_gf_log_callingfn()`, `_gf_log_eh()`, `_gf_smsg()`, and `_gf_msg_backtrace_nomem()`.

`gf_log_handle_t` stores mutexes, log level, syslog threshold, selected logger/format, file names, `FILE *` handles, duplicate-suppression LRU queue, timer handle, rotation flags, and localtime configuration. `log_buf_t` stores one suppressible message signature and repetition metadata.

## Control Flow
`gf_log_globals_init()` initializes mutexes, default levels, syslog defaults, logger and format defaults, the LRU queue, and syslog identity. `gf_log_init()` sets an optional ident, opens syslog, checks `/etc/glusterfs/logger.conf` to decide syslog-control behavior, creates the log directory, opens either stderr or an append log file, and updates `ctx->log`.

The main `_gf_msg()` path checks `THIS` and context availability, filters by translator/global log level, formats the application message, optionally captures a short backtrace, and routes to syslog if the file logger is not initialized or to `_gf_msg_internal()` otherwise. `_gf_msg_internal()` chooses direct output for calling-function traces or traditional format. For enhanced format, it searches the suppression LRU for an identical message signature; duplicates update refcount and latest timestamp, new messages are added and printed immediately, and LRU overflow flushes the oldest suppressed entry.

Output routing is split between `gf_log_syslog()` and `gf_log_glusterlog()`. File logging takes `logfile_mutex`, rotates when requested by `gf_log_rotate()`, writes a formatted line, flushes, and optionally mirrors severe logs to syslog. Suppression flushes are driven by buffer resize, explicit shutdown, or `gf_log_flush_timeout_cbk()` scheduled through the timer subsystem.

No-memory paths avoid heap allocation where possible: `_gf_msg_nomem()` writes a stack buffer directly to the log fd and then emits a backtrace via `backtrace_symbols_fd()`. `_gf_smsg()` builds event-style key/value text through `_do_slog_format()` and delegates to `_gf_msg()`.

## State And Persistence
The module mutates process-global logging state in `glusterfs_ctx_t->log` and implicitly uses thread-local/global `THIS`. Persistent side effects are append writes to the configured log file, command log, stderr, and syslog. Log rotation state is carried in `logrotate` and `cmd_history_logrotate` flags, often set from a signal handler. Duplicate suppression state lives in an in-memory LRU and is flushed before exit by `gf_log_disable_suppression_before_exit()`.

## Dependencies And Integration Points
Dependencies include pthreads, syslog, locale, time, resource usage, backtrace support, `glusterfs/syscall.h`, timers, `mem-pool` allocation, common utils, event history, and generated message IDs. The logging macros in `logging.h` are used throughout libglusterfs and translators. `gf_log_inject_timer_event()` depends on the context timer wheel. Command logging is used by management/glusterd paths.

## Risks
Logging runs in low-memory and failure paths, so accidental allocation in no-memory paths is high risk. `gf_log_logrotate()` is signal-facing and writes context flags through `THIS`; only async-signal-safe assumptions should be reviewed carefully. `_gf_log()` has older rotation logic separate from `gf_log_rotate()`, creating behavior drift. Duplicate suppression compares full formatted strings while holding `log_buf_lock`; expensive logging bursts can increase contention. Several functions assume `THIS` and `THIS->ctx` are valid. `_json_escape()` computes escaped text, but `gf_syslog()` currently syslogs the unescaped `msg`, so CEE-style JSON escaping is not fully realized. `_do_slog_format()` walks varargs by counting percent signs and can mis-handle unusual format strings or type mismatches.

## Test Signals
Coverage should include file and stderr initialization, missing parent directory creation, syslog-control-file behavior, log-level filtering, per-translator log level override, rotation races, enhanced versus traditional formats, duplicate suppression and LRU overflow, timer flush, shutdown flush, no-memory direct fd writes, command log rotation, structured `_gf_smsg()` formatting, backtrace inclusion, and operation before/after `gf_log_fini()`. Fault injection around `vasprintf`, `gf_asprintf`, `fdopen`, and `sys_open` is important.
