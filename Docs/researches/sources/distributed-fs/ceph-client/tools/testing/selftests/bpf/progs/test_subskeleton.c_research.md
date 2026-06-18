<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton.c

## Purpose

Main object for libbpf subskeleton linking tests, consuming variables and routines from companion library objects. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 28 source lines. BPF sections: `raw_tp/sys_enter`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `handler1`. Notable globals or configuration/result fields include `const volatile int rovar1`; `int out1`; `int var5 = 5`; `int handler1(const void *ctx)`.

## Control Flow

`handler1` combines `rovar1`, local `var5`, kconfig `CONFIG_BPF_SYSCALL`, and `lib_routine()` into `out1`.

## State And Persistence Behavior

Exports `out1` and `var5`; imports `lib_routine` and kconfig extern state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Cross-object extern resolution, weak variable handling, and kconfig relocations must survive subskeleton generation. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The subskeleton harness should set rodata, load linked objects, trigger the raw tracepoint, and verify `out1`. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton.c -->
