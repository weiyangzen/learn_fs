# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_send_signal_kern.c

Research item: `subset-b-006814` ordinal `111`. Source size: 1531 bytes. Final artifact: `/home/sansha-2/Github/learn_fs/Docs/researches/sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_send_signal_kern.c_research.md`.

## Purpose
The file attaches tracepoint or raw tracepoint programs to inspect kernel event arguments and collect test-visible state. It lives under Linux `tools/testing/selftests/bpf/progs`, so it is compiled into a BPF object and driven by a matching selftest harness rather than being production Ceph-client code.

## Important APIs, Types, And Functions
- Attach sections: `tracepoint/syscalls/sys_enter_nanosleep`, `tracepoint/sched/sched_switch`, `perf_event`
- BPF helpers/macros used: `bpf_helpers`, `bpf_task_from_pid`, `bpf_task_release`, `bpf_send_signal_task`, `bpf_send_signal_test`, `bpf_get_current_pid_tgid`, `bpf_send_signal_thread`, `bpf_send_signal`
- Declared maps: None visible in this compact source.
- Key local types: `struct task_struct`, `enum pid_type`
- Main functions/subprograms: `bpf_task_release`, `bpf_send_signal_task`, `bpf_send_signal_test`, `send_signal_tp`, `send_signal_tp_sched`, `send_signal_perf`

## Control Flow
Entry programs are attached through `tracepoint/syscalls/sys_enter_nanosleep`, `tracepoint/sched/sched_switch`, `perf_event`. Control is organized around `bpf_task_release`, `bpf_send_signal_task`, `bpf_send_signal_test`, `send_signal_tp`, `send_signal_tp_sched`, `send_signal_perf`. State is mostly stack/local or global test data, with helper routines inlined by clang for verifier-friendly code generation. Branching is dominated by verifier-visible guard checks before pointer dereferences, helper calls, or map-value use.

## State And Persistence Behavior
Global data/control fields include `sig`, `__license`. There is no filesystem persistence; observable state is verifier load success, return value, or BSS/data globals read by the harness.

## Dependencies And Integration Points
This source depends on kernel UAPI/libbpf headers `vmlinux.h`, `linux/version.h`, `bpf/bpf_helpers.h`.
Local test dependencies: None visible in this compact source.
Integration is through the BPF selftest build system, libbpf skeleton/object loading, and the matching user-space test that populates maps, attaches sections, triggers kernel events or packets, and inspects globals/maps/logs.

## Risks And Review Notes
Tracepoint ABI changes, argument casting, stack capture flags, and helper restrictions can affect results.
Because this is verifier-facing code, seemingly small rewrites can change register bounds, pointer provenance, stack depth, BTF relocation records, or expected verifier log text. Keep helper calls, section names, map definitions, and feature guards aligned with the selftest harness.

## Test Signals
`test_send_signal_kern.c` is a test fixture for tracepoint/raw tracepoint BPF selftest. Test signals are: the user-space selftest validates load/attach success, map contents, global variables, or return codes.
High-signal code markers observed: `#include <bpf/bpf_helpers.h>` | `struct task_struct *bpf_task_from_pid(int pid) __ksym;` | `void bpf_task_release(struct task_struct *p) __ksym;` | `int bpf_send_signal_task(struct task_struct *task, int sig, enum pid_type type, u64 value) __ksym;` | `static __always_inline int bpf_send_signal_test(void *ctx)` | `if ((bpf_get_current_pid_tgid() >> 32) == pid) {` | `target_task = bpf_task_from_pid(target_pid);` | `ret = bpf_send_signal_task(target_task, sig, PIDTYPE_PID, value);` | `ret = bpf_send_signal_thread(sig);` | `ret = bpf_send_signal_task(target_task, sig, PIDTYPE_TGID, value);` | and 7 more marker lines
