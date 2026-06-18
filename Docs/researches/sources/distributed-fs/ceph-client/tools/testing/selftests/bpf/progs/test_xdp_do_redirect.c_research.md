<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_do_redirect.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_do_redirect.c

## Purpose

Tests XDP redirect helper behavior and packet marking across XDP and TC receive paths. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 128 source lines. BPF sections: `xdp`, `xdp`, `xdp`, `xdp`, `tc`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_helpers`, `bpf_redirect`, `bpf_xdp_adjust_meta`. Important C functions and entry points include `xdp_redirect`, `xdp_count_pkts`, `xdp_redirect_to_111`, `xdp_redirect_to_222`, `tc_count_pkts`. Notable globals or configuration/result fields include `const volatile int ifindex_out`; `const volatile int ifindex_in`; `const volatile __u8 expect_dst[ETH_ALEN]`; `volatile int pkts_seen_xdp = 0`; `volatile int pkts_seen_zero = 0`; `volatile int pkts_seen_tc = 0`; `volatile int retcode = XDP_REDIRECT`; `int xdp_redirect(struct xdp_md *xdp)`.

## Control Flow

The main XDP program adjusts metadata/marks frames, redirects to configured ifindexes, and counter programs validate expected destination MAC and mark values.

## State And Persistence Behavior

`ifindex_out`, `ifindex_in`, `expect_dst`, packet counters, and `retcode` are user-space controlled/observed globals. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Redirect completion, metadata preservation, and TC visibility after redirect are topology-dependent. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Send marked frames through the veth setup and verify XDP/TC counters. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_xdp_do_redirect.c -->
