## sources/distributed-fs/eos/mgm/ofs/cmds/Stacktrace.inc

Purpose: signal handler that prints diagnostic stack traces and optionally generates a core file before process termination or signal re-raise.

Important APIs and types: `xrdmgmofs_stacktrace`, `backtrace`, `backtrace_symbols_fd`, `eos::common::StackTrace::GdbTrace`, environment variables `EOS_CORE_DUMP` and `EOS_RAISE_SIGNAL_AFTER_SIGV`, `kill`, and `std::quick_exit`.

Control flow: ignores common termination signals, captures up to ten stack frames, prints the received signal and frame symbols to stderr, asks gdb for `thread apply all bt`, optionally asks gdb to `generate-core-file`, then either restores the default handler and re-sends the original signal or exits with `128 + sig`.

State and persistence behavior: normally no namespace state. It can create a core file when configured and always writes diagnostics to stderr. It exits without normal destructor unwinding unless configured to re-raise.

Dependencies and integration points: registered for crash diagnostics in the MGM process and depends on gdb availability/permissions through `StackTrace::GdbTrace`.

Risks: stack tracing, gdb invocation, environment checks, and stdio are not async-signal-safe. Capturing only ten direct frames may be less useful than the gdb all-thread trace. Core-file generation can be large, which the code avoids by default.

Test signals: handler prints frame information, gdb trace command invocation under normal mode, `EOS_CORE_DUMP` triggers core command, `EOS_RAISE_SIGNAL_AFTER_SIGV` re-raises with default handler, and default path exits with `128 + sig`.
