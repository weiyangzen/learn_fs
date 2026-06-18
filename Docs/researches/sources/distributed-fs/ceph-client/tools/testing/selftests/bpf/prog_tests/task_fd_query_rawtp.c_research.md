# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/task_fd_query_rawtp.c

Purpose: validates `bpf_task_fd_query` metadata for a raw tracepoint attachment. It loads `test_get_stack_rawtp.bpf.o`, opens raw tracepoint `sys_enter`, and queries the resulting fd.

Control flow loads the raw tracepoint program, calls `bpf_raw_tracepoint_open`, then queries current process and fd with normal buffer, zero-length buffer, NULL buffer, and too-small buffer. State is the raw tracepoint fd, program object, output buffer, and returned metadata fields. Dependencies are raw tracepoint support and `bpf_task_fd_query`. Risks include missing close for raw tracepoint fd in this harness and exact truncation semantics. Test signals are `fd_type == BPF_FD_TYPE_RAW_TRACEPOINT`, name `sys_enter`, zero/NULL buffer returning required length, and small buffer returning `ENOSPC` with truncated `"sy"`.
