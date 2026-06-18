<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.h

## Purpose

Provides checksum, endian, array-swap, and unaligned access helpers shared by the custom syncookie BPF program. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 138 source lines. BPF sections: none. Map types declared or referenced: none. Important helper/kfunc surface: `bpf_htonl`, `bpf_ntohl`, `bpf_ntohs`. Important C functions and entry points include no ordinary C entry points detected. Notable globals or configuration/result fields include no notable globals.

## Control Flow

Inline routines fold checksums, compute IPv4/IPv6 TCP pseudo-header checksums, swap fields, and fetch unaligned big-endian values.

## State And Persistence Behavior

Header-only helpers have no persistent state. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

A small arithmetic or endian bug here invalidates all syncookie packet validation and generation. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Signals are indirect through `test_tcp_custom_syncookie.c` handshakes and checksum validation. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_custom_syncookie.h -->
