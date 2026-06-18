<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stack_var_off.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stack_var_off.c

## Purpose

Verifier test for variable-offset stack writes followed by variable-offset stack reads. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 51 source lines. BPF sections: `tracepoint/syscalls/sys_enter_nanosleep`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_get_current_pid_tgid`, `bpf_helpers`. Important C functions and entry points include `probe`. Notable globals or configuration/result fields include `int probe_res`; `char input[4] = {}`; `int test_pid`; `int probe(void *ctx)`.

## Control Flow

A nanosleep tracepoint filters on `test_pid`, copies four bytes of global `input` to a stack buffer, derives a variable length, writes byte 42 at that variable offset, and stores a variable-offset read into `probe_res`.

## State And Persistence Behavior

`input`, `test_pid`, and `probe_res` are BSS/data signals controlled and read by user space. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The verifier must reason about stack initialization conservatively without rejecting the intended write-then-read pattern. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Drive nanosleep in the selected process and check `probe_res` matches the expected stack byte. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stack_var_off.c -->
