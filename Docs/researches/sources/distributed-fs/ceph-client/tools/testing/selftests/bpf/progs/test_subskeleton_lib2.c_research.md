<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton_lib2.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton_lib2.c

## Purpose

Small second library object supplying `var6` and `map2` for the subskeleton link graph. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 16 source lines. BPF sections: `.maps`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include no ordinary C entry points detected. Notable globals or configuration/result fields include `int var6 = 6`.

## Control Flow

No program section is present; the object contributes data and a hash map for other objects to reference.

## State And Persistence Behavior

`var6` and `map2` are persistent linked-object state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Object files without programs still need BTF/map/data handling and extern resolution. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Successful link/load and visibility of `var6`/`map2` through the composite skeleton are the key signals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_subskeleton_lib2.c -->
