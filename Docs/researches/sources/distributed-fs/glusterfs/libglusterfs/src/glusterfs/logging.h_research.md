# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/logging.h

Purpose: `logging.h` declares GlusterFS logging levels, output formats, logger backends, runtime log handle state, suppression buffers, and the public macros used throughout translators and libglusterfs.

Important APIs and types: `gf_loglevel_t` spans none/emerg/alert/critical/error/warning/notice/info/debug/trace. `gf_log_handle_t` stores mutexes, current levels, syslog toggles, filenames, `FILE *` handles, logger/format choices, suppression LRU state, flush timer, and rotate flags. `log_buf_t` records suppressed message metadata. Core functions include `gf_log_globals_init`, `gf_log_init`, `gf_log_cleanup`, `_gf_msg`, `_gf_log`, `gf_log_set_loglevel`, `gf_log_flush`, command-log helpers, suppression tuning, and structured `_gf_smsg`.

Control flow and state: macros such as `gf_msg`, `gf_msg_debug`, `gf_msg_trace`, `gf_log`, `GF_DEBUG`, and `GF_LOG_*` capture file/function/line and delegate to implementation functions. State is process/global-context scoped through `glusterfs_ctx_t` and, for structured macros, `global_ctx`.

Dependencies and integration: logging is foundational for graph parsing, option validation, memory allocation failures, runner operations, and graph lifecycle diagnostics. It depends on list handling, timers, pthread mutexes, and message-id headers.

Risks: macros evaluate variadic arguments at call sites and can hide control flow. Structured `GF_LOG*` macros require `global_ctx` and generated message definitions. Suppression, rotation, and flush timers are shared mutable state and need careful shutdown ordering.

Test signals: validate log-level filtering, message-id formatting, syslog enable/disable, rotate flags, suppression buffer limits, no-allocation `gf_msg_nomem` paths, and structured log macro builds with generated message headers.
