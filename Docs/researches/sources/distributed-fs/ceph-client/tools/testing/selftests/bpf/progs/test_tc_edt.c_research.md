<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_edt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_edt.c

## Purpose

Implements a small earliest-departure-time shaper and ECN marker in TC. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 111 source lines. BPF sections: `.maps`, `tc`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_htons`, `bpf_ktime_get_ns`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_skb_ecn_set_ce`. Important C functions and entry points include `tc_prog`. Notable globals or configuration/result fields include `int tc_prog(struct __sk_buff *skb)`.

## Control Flow

For selected TCP/IPv4 packets, it tracks flow timestamp in `flow_map`, sets `skb->tstamp` for pacing, and marks ECN CE when the delay exceeds a threshold.

## State And Persistence Behavior

`flow_map` persists one flow's next departure time. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Time arithmetic, GSO behavior, and ECN helper return values can vary with packet shape. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should inspect pacing timestamps and ECN marking under repeated TCP traffic. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tc_edt.c -->
