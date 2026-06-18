<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked2.c

## Purpose

Companion static-linking object with same static function name but a different formula and data layout. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 31 source lines. BPF sections: `raw_tp/sys_enter`, `license`, `version`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `handler2`. Notable globals or configuration/result fields include `int var2 = -1`; `const volatile long rovar2`; `int handler2(const void *ctx)`.

## Control Flow

`handler2` computes `var2 = subprog(rovar2) + static_var1 + static_var2`, where this file's `subprog` triples its input.

## State And Persistence Behavior

Uses file-local statics plus externally visible `var2` and `rovar2`; license/version names intentionally differ from the first object. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The linker must keep duplicate static functions independent and merge BPF metadata without changing symbol visibility. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The linked skeleton should run both raw tracepoint handlers and report distinct formulas for `var1` and `var2`. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked2.c -->
