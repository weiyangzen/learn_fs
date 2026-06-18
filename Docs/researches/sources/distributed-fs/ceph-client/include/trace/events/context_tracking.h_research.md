# sources/distributed-fs/ceph-client/include/trace/events/context_tracking.h

## Purpose
`context_tracking.h` traces transitions between kernel and userspace context tracking.

## Important APIs, types, and functions
It defines the `context_tracking_user` event class and two events: `user_enter` and `user_exit`. The dummy integer field exists to satisfy trace event macro requirements.

## Control flow
`user_enter` fires when the kernel resumes to userspace after a syscall or exception. `user_exit` fires when userspace enters the kernel through a syscall or exception.

## State and persistence behavior
The header owns no state and records only a dummy field; the useful information is timestamp, CPU, task, and ordering supplied by the tracing framework.

## Dependencies and integration points
It depends on `<linux/tracepoint.h>` and context tracking call sites. It integrates with RCU/nohz/context-tracking diagnostics.

## Risks and test signals
Risks include very high event volume and low payload detail. Test signals are syscall/exception workloads where user exit precedes kernel work and user enter follows return-to-user paths.
