<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_hdr_options.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_hdr_options.c

## Purpose

Comprehensive sockops test for reserving, writing, parsing, and resending custom TCP header options across SYN, SYNACK, data, FIN, syncookie, and fastopen paths. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 623 source lines. BPF sections: `.maps`, `sockops`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_SK_STORAGE`. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_load_hdr_opt`, `bpf_misc`, `bpf_reserve_hdr_opt`, `bpf_setsockopt`, `bpf_sk_storage_get`, `bpf_sock_ops`, `bpf_sock_ops_cb_flags`, `bpf_store_hdr_opt`, `bpf_test_option`. Important C functions and entry points include `estab`. Notable globals or configuration/result fields include `__u32 inherit_cb_flags = 0`; `int estab(struct bpf_sock_ops *skops)`.

## Control Flow

Sockops callbacks route by `skops->op`; they reserve option space, write experimental or regular options, parse peer options, store per-socket state in SK_STORAGE, and adjust delayed-ACK/RTO settings with `bpf_setsockopt`.

## State And Persistence Behavior

Many global `bpf_test_option` structs capture active/passive inbound/outbound options; `hdr_stg_map` persists per-socket active/passive/resend/syncookie/fastopen state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Header option length accounting, callback flag inheritance, saved-SYN lookup, syncookie resend, and TCP fastopen can each regress independently. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should run active/passive connections with configured option flags and verify all global option result structs and cb-flag behavior. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_hdr_options.c -->
