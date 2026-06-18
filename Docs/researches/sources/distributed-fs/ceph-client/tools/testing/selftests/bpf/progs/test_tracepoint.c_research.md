<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tracepoint.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tracepoint.c

## Purpose

Basic tracepoint context test for `sched:sched_switch`. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 25 source lines. BPF sections: `tracepoint/sched/sched_switch`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `oncpu`. Notable globals or configuration/result fields include `int oncpu(struct sched_switch_args *ctx)`.

## Control Flow

The tracepoint program reads scheduler switch context fields and returns.

## State And Persistence Behavior

No long-lived map state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Tracepoint context layout is ABI-sensitive but normally stable through generated format/BTF data. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attach and trigger context switches; successful verifier load is the primary signal. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tracepoint.c -->
