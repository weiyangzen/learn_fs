<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_cookie.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_cookie.c

Purpose: Exercises `bpf_get_attach_cookie` across many attach types.

Important APIs/types/functions: Defines `update` helper and handlers for kprobe, kretprobe, uprobe, uretprobe, tracepoint variants, perf_event, raw_tp, tp_btf, fentry/fexit/fmod_ret, and LSM.

Control flow: Each handler reads the attach cookie and records it in global slots for userspace validation.

State and persistence: Persistent state is global cookie/result variables.

Dependencies and integration: Depends on attach-cookie support across tracing, perf, and LSM program types.

Risks: Some attach types have distinct cookie plumbing; regressions show as zero or wrong cookie values.

Test signals: Tests attach with known cookies and compare recorded values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_bpf_cookie.c -->
