<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt.c

## Purpose

Exercises generic and fully specified USDT attach paths, argument count/size accessors, cookies, and typed argument reads. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 153 source lines. BPF sections: `usdt`, `usdt//proc/self/exe:test:usdt3`, `usdt//proc/self/exe:test:usdt12`, `usdt`, `usdt`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_for`, `bpf_get_current_pid_tgid`, `bpf_get_prandom_u32`, `bpf_helpers`, `bpf_usdt_arg`, `bpf_usdt_arg_cnt`, `bpf_usdt_arg_size`, `bpf_usdt_cookie`. Important C functions and entry points include `usdt0`, `usdt3`, `BPF_USDT`, `usdt_sib`, `usdt_executed`. Notable globals or configuration/result fields include `int my_pid`; `int usdt0_called`; `int usdt0_arg_cnt`; `int usdt0_arg_ret`; `int usdt0_arg_size`; `int usdt0(struct pt_regs *ctx)`; `int usdt3_called`; `int usdt3_arg_cnt`.

## Control Flow

USDT programs read pid, cookies, argument counts and values via `bpf_usdt_arg*`, including looped argument handling.

## State And Persistence Behavior

Globals record probe hits, argument values, sizes, and cookies. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Argument decoding depends on architecture-specific USDT notes and register/stack locations. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Trigger probes with 3 and 12 arguments and verify all captured metadata. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_usdt.c -->
