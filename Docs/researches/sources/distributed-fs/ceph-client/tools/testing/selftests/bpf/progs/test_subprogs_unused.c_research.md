<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs_unused.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs_unused.c

## Purpose

Ensures unused noinline subprograms do not break loading or CO-RE relocation handling. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 21 source lines. BPF sections: `license`, `raw_tp/sys_enter`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_core_read`, `bpf_helpers`. Important C functions and entry points include `main_prog`. Notable globals or configuration/result fields include `int main_prog(void *ctx)`.

## Control Flow

`main_prog` is a raw tracepoint program; unused functions remain in source but should not affect runtime behavior.

## State And Persistence Behavior

No meaningful runtime state beyond license metadata. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Dead-code elimination and BTF/function info generation must not leave dangling relocations for unused functions. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Successful load and attach is the primary signal. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subprogs_unused.c -->
