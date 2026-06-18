# File Research: sources/cow-pools/bcachefs-tools/include/trace/events/lock.h

Defines lock trace event declarations and contention flag constants. Under `CONFIG_LOCKDEP` it describes acquire/release/contended/acquired events; outside that, only contention begin/end events remain.

Because `linux/tracepoint.h` stubs trace macros, these compile into no-op trace functions in this userspace tree.
