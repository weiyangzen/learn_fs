# File Research: sources/cow-pools/bcachefs-tools/include/linux/tracepoint.h

Implements tracepoint macros as inert stubs. `DECLARE_TRACE` and `TRACE_EVENT` generate no-op trace functions, register/unregister returning `-ENOSYS`, and enabled checks returning false.

This allows trace-event headers to compile without runtime tracing support.
