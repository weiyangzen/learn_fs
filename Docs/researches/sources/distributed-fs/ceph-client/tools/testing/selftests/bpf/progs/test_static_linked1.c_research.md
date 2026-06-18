<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked1.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked1.c

## Purpose

One half of a static-linking test with duplicate static symbol names and distinct data/rodata alignment. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 30 source lines. BPF sections: `raw_tp/sys_enter`, `license`, `version`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `handler1`. Notable globals or configuration/result fields include `int var1 = -1`; `const volatile int rovar1`; `int handler1(const void *ctx)`.

## Control Flow

`handler1` computes `var1 = subprog(rovar1) + static_var1 + static_var2`, using this file's static `subprog` that doubles its input.

## State And Persistence Behavior

Static variables remain file-local after linking, while `var1` and `rovar1` are externally visible skeleton state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Static symbol collision, data-section alignment, and license/version symbol merging are the important linker edges. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

After static linking with the companion object, setting `rovar1` and triggering `raw_tp/sys_enter` should update only `var1` with the doubled formula. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_static_linked1.c -->
