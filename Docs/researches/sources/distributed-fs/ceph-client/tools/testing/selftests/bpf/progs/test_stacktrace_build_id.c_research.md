<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stacktrace_build_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stacktrace_build_id.c

## Purpose

Tests user stack collection with build IDs through stack trace maps. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 67 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `.maps`, `kprobe/urandom_read_iter`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_HASH`, `BPF_MAP_TYPE_STACK_TRACE`. Important helper/kfunc surface: `bpf_get_stack`, `bpf_get_stackid`, `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_stack_build_id`. Important C functions and entry points include `oncpu`. Notable globals or configuration/result fields include `int oncpu(struct pt_regs *args)`.

## Control Flow

A kprobe on `urandom_read_iter` skips when `control_map[0]` is nonzero, gets a user stack id into a build-id stack map, records the id in a hash, then copies stack frames into an array map.

## State And Persistence Behavior

`control_map` gates collection; `stackid_hmap`, `stackmap`, and `stack_amap` persist captured stack IDs and build-id frame arrays. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

User-stack capture depends on process mappings and build IDs; map size and `PERF_MAX_STACK_DEPTH` must align across stackid and raw stack copies. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should trigger the kprobe through urandom reads and validate non-empty stack ID/build-id records. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_stacktrace_build_id.c -->
