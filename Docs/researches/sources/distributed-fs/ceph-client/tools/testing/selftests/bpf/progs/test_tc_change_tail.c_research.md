<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_change_tail.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_change_tail.c

## Purpose

Tests `bpf_skb_change_tail` and data pointer invalidation for TC ingress packets. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 106 source lines. BPF sections: `tc/ingress`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_skb_change_tail`, `bpf_skb_pull_data`. Important C functions and entry points include `change_tail`. Notable globals or configuration/result fields include `long change_tail_ret = 1`; `int change_tail(struct __sk_buff *skb)`.

## Control Flow

The program parses IPv4/UDP headers, pulls data, changes packet tail up to bounded sizes, reparses after helper calls, and stores `change_tail_ret`.

## State And Persistence Behavior

`change_tail_ret` is the user-visible result; packet data is mutated transiently. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Helpers that reallocate skb data invalidate direct packet pointers; all reparsing and length bounds must be correct. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Feed UDP/IP packets and assert return code plus packet length changes. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_change_tail.c -->
