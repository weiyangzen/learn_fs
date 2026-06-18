<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trace_ext_tracing.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trace_ext_tracing.c

## Purpose

Tracing companion for extension tests, attaching fentry and fexit to `test_pkt_md_access_new`. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 25 source lines. BPF sections: `fentry/test_pkt_md_access_new`, `fexit/test_pkt_md_access_new`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_tracing`. Important C functions and entry points include `BPF_PROG`, `BPF_PROG`. Notable globals or configuration/result fields include `__u64 fentry_called = 0`; `int BPF_PROG(fentry, struct sk_buff *skb)`; `__u64 fexit_called = 0`; `int BPF_PROG(fexit, struct sk_buff *skb)`.

## Control Flow

The entry and exit programs record that the target function was entered/exited and can inspect return values.

## State And Persistence Behavior

State is minimal global result flags/counters in the object. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Fentry/fexit target resolution must work for extension-created symbols. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Invoke the target and check both tracing programs ran. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_trace_ext_tracing.c -->
