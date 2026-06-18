<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_vmlinux.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_vmlinux.c

## Purpose

Exercises vmlinux BTF type access across tracepoint, raw tracepoint, tp_btf, kprobe, and fentry programs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 90 source lines. BPF sections: `tp/syscalls/sys_enter_nanosleep`, `raw_tp/sys_enter`, `tp_btf/sys_enter`, `kprobe/hrtimer_start_range_ns`, `fentry/hrtimer_start_range_ns`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_core_read`, `bpf_helpers`, `bpf_probe_read_user`, `bpf_tracing`. Important C functions and entry points include `handle__tp`, `BPF_PROG`, `BPF_PROG`, `BPF_KPROBE`, `BPF_PROG`. Notable globals or configuration/result fields include `bool tp_called = false`; `bool raw_tp_called = false`; `bool tp_btf_called = false`; `bool kprobe_called = false`; `bool fentry_called = false`; `int handle__tp(struct syscall_trace_enter *args)`; `int BPF_PROG(handle__raw_tp, struct pt_regs *regs, long id)`; `int BPF_PROG(handle__tp_btf, struct pt_regs *regs, long id)`.

## Control Flow

Handlers read syscall and hrtimer context using BTF-defined types and probe/user read helpers.

## State And Persistence Behavior

Globals record observed values from the different attach points. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

BTF type names and context layouts must match the running kernel. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger nanosleep/hrtimer paths and validate all BTF-based reads succeed. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_vmlinux.c -->
