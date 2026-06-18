<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe.c

Purpose: Comprehensive auto-attach probe test for ksyscall/kretsyscall, uprobes/uretprobes by name, ref counters, and sleepable user-copy helpers.

Important APIs/types/functions: Defines result globals, kprobe/retprobe handlers, uprobe/uretprobe handlers, `verify_sleepable_user_copy`, and `verify_sleepable_user_copy_str`.

Control flow: Handlers set distinct globals; sleepable handlers copy user buffers and validate truncation, zero padding, dynamic sizes, invalid flags, and fault behavior.

State and persistence: Persistent state is result globals and `user_ptr`/`dynamic_sz` inputs set by userspace.

Dependencies and integration: Depends on libbpf auto-attach section parsing, probe macros, weak `bpf_copy_from_user_str`, and sleepable uprobe support.

Risks: User pointer safety, mixed sleepable/non-sleepable arrays, and section-name parsing are risks.

Test signals: Tests trigger nanosleep and process-local functions, then inspect all result globals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_attach_probe.c -->
