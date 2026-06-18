<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_progs_query.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_progs_query.c

## Purpose

Provides minimal `sk_skb` and `sk_msg` verdict programs attached to a one-entry SOCKMAP so user space can query which programs are attached to a sockmap. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 24 source lines. BPF sections: `.maps`, `sk_skb`, `sk_msg`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_SOCKMAP`. Important helper/kfunc surface: `bpf_helpers`. Important C functions and entry points include `prog_skb_verdict`, `prog_skmsg_verdict`. Notable globals or configuration/result fields include `int prog_skb_verdict(struct __sk_buff *skb)`; `int prog_skmsg_verdict(struct sk_msg_md *msg)`.

## Control Flow

Both programs return `SK_PASS` without inspecting packet or message data; the test signal is attachment/query metadata rather than packet transformation.

## State And Persistence Behavior

The only persistent kernel state is the `sock_map` and its attached program links. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Regressions usually show up as wrong attach type reporting, section-name handling changes, or libbpf failing to bind the program to SOCKMAP-compatible hooks. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

A passing selftest should load both programs, attach them to the map, query map programs, and observe `SK_PASS` behavior. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_progs_query.c -->
