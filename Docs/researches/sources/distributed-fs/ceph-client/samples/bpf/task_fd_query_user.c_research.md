<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/task_fd_query_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/task_fd_query_user.c

## Purpose
`task_fd_query_user.c` is a userspace validation harness for `bpf_task_fd_query()`. It loads the matching kernel BPF object, attaches kprobe/kretprobe and uprobe/uretprobe programs through both tracefs/debugfs and perf-event PMU paths, then verifies that the kernel reports the expected probe target name, fd type, offset, address, and program id.

## Important APIs, Types, And Functions
Important routines are `bpf_find_probe_type()`, `bpf_get_retprobe_bit()`, `test_debug_fs_kprobe()`, `test_nondebug_fs_kuprobe_common()`, `test_nondebug_fs_probe()`, `test_debug_fs_uprobe()`, and `main()`. It uses `bpf_object__open_file()`, `bpf_object__load()`, `bpf_program__attach()`, `bpf_program__attach_perf_event()`, `bpf_task_fd_query()`, `sys_perf_event_open()`, `load_kallsyms()`, and `ksym_get_addr()`.

## Control Flow
Startup loads kallsyms, opens `<argv[0]>_kern.o`, loads all BPF programs, and attaches them as libbpf links. The debugfs kprobe checks query the fd returned by an attached `bpf_link`. Non-debugfs tests discover PMU type and retprobe config bits from sysfs, create perf events by symbol, offset, or absolute address, attach a program to each fd, and call `bpf_task_fd_query()`. Debugfs uprobe testing writes a temporary event to `uprobe_events`, opens the generated tracepoint id as a perf event, attaches BPF, and validates query metadata.

## State And Persistence
Persistent process state is limited to two arrays of `struct bpf_program *` and `struct bpf_link *`. Kernel-visible temporary state includes perf-event fds, tracefs probe definitions, and libbpf links; all links are destroyed on cleanup. No long-lived BPF map data is managed here.

## Dependencies And Integration Points
The harness depends on libbpf, `bpf_util.h`, `perf-sys.h`, `trace_helpers.h`, `/proc/kallsyms`, `/sys/bus/event_source/devices/{kprobe,uprobe}`, `/sys/kernel/tracing`, and kernel support for BPF task fd querying. It integrates with the companion task-fd-query kernel sample object and the perf event subsystem.

## Risks And Edge Cases
The uprobe file-offset calculation relies on `main - __executable_start`, which the comments acknowledge is linker/compiler dependent. Tracefs permissions, disabled kallsyms, unavailable PMUs, architecture-specific offsets, stale probe aliases, and short query buffers can all cause false failures. Error exits through macros can bypass some cleanup in inner helpers.

## Test Signals
Success is all `CHECK_AND_RET()` calls returning zero and process exit status zero. Useful signals include correct fd type for kprobe/kretprobe/uprobe/uretprobe, zero buffer length behavior for address-only probes, x86 offset coverage, tracefs event cleanup, and running under kernels with and without debugfs-style probe creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/task_fd_query_user.c -->
