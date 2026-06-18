<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_update.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_update.c

## Purpose

Verifies that a socket obtained from one SOCKMAP can be inserted into another SOCKMAP and into a SOCKHASH from BPF. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 48 source lines. BPF sections: `.maps`, `.maps`, `.maps`, `tc`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_SOCKHASH`, `BPF_MAP_TYPE_SOCKMAP`. Important helper/kfunc surface: `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_sk_release`, `bpf_sock`. Important C functions and entry points include `copy_sock_map`. Notable globals or configuration/result fields include `int copy_sock_map(void *ctx)`.

## Control Flow

`copy_sock_map` looks up key 0 in `src`, updates both destination maps with that socket pointer, releases it, and returns `SK_PASS` or `SK_DROP` based on helper failures.

## State And Persistence Behavior

The source and destination maps persist socket references; the program must release the lookup reference with `bpf_sk_release`. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Reference balancing is the key safety point; missing release or invalid update target would cause verifier or runtime errors. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should populate `src`, run the TC program, and check destination sockmap/sockhash entries exist. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_sockmap_update.c -->
