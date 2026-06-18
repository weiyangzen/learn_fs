# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/peeksiginfo.c

Purpose: tests `PTRACE_PEEKSIGINFO` for private and shared pending signal queues and selected error paths.

Important APIs and functions: raw `rt_sigqueueinfo`, `rt_tgsigqueueinfo`, and `ptrace`; `check_direct_path()` validates queued siginfo order/content; `check_error_paths()` validates unsupported flags and inaccessible output buffers using `mmap`.

Control flow: block `SIGRTMIN`, fork a sleeping child, enqueue ten process-wide and ten thread-directed real-time signals with distinct `si_code` and `si_int`, attach to child, read private queue one at a time and all at once, read shared queue in chunks of three, test error paths, then kill tracee.

State and persistence: pending signals on the child are the tested state.

Dependencies and integration: depends on realtime signals, ptrace attach permission, and memory protection faults.

Risks and test signals: signal queue limits or permission settings can affect setup. Failures indicate wrong queue selection, ordering, copying, or errno behavior for peeksiginfo.
