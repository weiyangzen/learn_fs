<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpbpf_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpbpf_kern.c

## Purpose

Sockops test for TCP BPF callbacks, socket options, and TCP socket field access. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 154 source lines. BPF sections: `sockops`, `license`. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_endian`, `bpf_getsockopt`, `bpf_helpers`, `bpf_setsockopt`, `bpf_skc_to_tcp_sock`, `bpf_sock`, `bpf_sock_ops`, `bpf_sock_ops_cb_flags_set`, `bpf_testcb`, `bpf_tracing_net`. Important C functions and entry points include `bpf_testcb`. Notable globals or configuration/result fields include `int bpf_testcb(struct bpf_sock_ops *skops)`.

## Control Flow

The sockops program handles connection state callbacks, sets callback flags, uses get/set sockopt helpers, reads TCP socket fields through `bpf_skc_to_tcp_sock`, and updates shared globals from `bpf_globals.h`.

## State And Persistence Behavior

Observable state is stored in included globals/test callback structures. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Sockops callback ordering and writable options differ across TCP states; field access requires valid socket type conversion. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Run TCP client/server selftest and compare callback counters and option values. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpbpf_kern.c -->
