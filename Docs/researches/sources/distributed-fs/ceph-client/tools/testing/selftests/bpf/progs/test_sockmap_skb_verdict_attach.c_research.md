<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_skb_verdict_attach.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_skb_verdict_attach.c

## Purpose

Checks explicit `sk_skb/verdict` section attachment against a SOCKMAP. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 18 source lines. BPF sections: `.maps`, `sk_skb/verdict`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_SOCKMAP`. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `prog_skb_verdict`. Notable globals or configuration/result fields include `int prog_skb_verdict(struct __sk_buff *skb)`.

## Control Flow

The verdict program always returns `SK_DROP`, giving user space a deterministic result when the attach succeeds.

## State And Persistence Behavior

A two-entry `sock_map` is the only map state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

The main edge case is section-name compatibility between older `sk_skb` and explicit `sk_skb/verdict` forms. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Successful load, attach, and traffic drop confirm the expected attach-type path. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_skb_verdict_attach.c -->
