<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_link.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_link.c

## Purpose

Covers TC link attach ordering, ingress/egress section handling, skb mark/priority propagation, packet type mutation, and CO-RE field reads. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 129 source lines. BPF sections: `license`, `tc/ingress`, `tc/egress`, `tc/egress`, `tc/egress`, `tc/egress`, `tc/egress`, `tc/ingress`, `tc/egress`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_core_read`, `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_skb_change_type`, `bpf_skb_load_bytes`, `bpf_skb_store_bytes`. Important C functions and entry points include `tc1`, `tc2`, `tc3`, `tc4`, `tc5`, `tc6`, `tc7`, `tc8`. Notable globals or configuration/result fields include `bool seen_tc1`; `bool seen_tc2`; `bool seen_tc3`; `bool seen_tc4`; `bool seen_tc5`; `bool seen_tc6`; `bool seen_tc7`; `bool seen_tc8`.

## Control Flow

Multiple TC programs set `seen_tc*` globals, change skb type, inspect Ethernet packet type, update mark/prio, and read nested skb/net_device fields.

## State And Persistence Behavior

Boolean globals and `mark`/`prio` are the observable test state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

TC link replacement/order and context field writeability are attachment-sensitive. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Attach all links, send packets through ingress/egress, and assert the seen flags and context mutations. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_link.c -->
