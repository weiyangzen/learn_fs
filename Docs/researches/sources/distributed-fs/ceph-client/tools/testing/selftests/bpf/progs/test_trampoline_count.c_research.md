<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trampoline_count.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trampoline_count.c

## Purpose

Tests multiple BPF trampoline attachment kinds on one bpf_testmod function. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 24 source lines. BPF sections: `fentry/bpf_testmod_trampoline_count_test`, `fmod_ret/bpf_testmod_trampoline_count_test`, `fexit/bpf_testmod_trampoline_count_test`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_testmod_trampoline_count_test`, `bpf_tracing`. Important C functions and entry points include `BPF_PROG`, `BPF_PROG`, `BPF_PROG`. Notable globals or configuration/result fields include `int BPF_PROG(fentry_test)`; `int BPF_PROG(fmod_ret_test, int ret)`; `int BPF_PROG(fexit_test, int ret)`.

## Control Flow

Fentry, fmod_ret, and fexit programs attach to `bpf_testmod_trampoline_count_test` and return in their respective phases.

## State And Persistence Behavior

No maps; trampoline accounting is kernel state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The kernel must count and order mixed trampoline programs correctly. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attach all programs and invoke the testmod function, expecting trampoline count assertions to pass. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trampoline_count.c -->
