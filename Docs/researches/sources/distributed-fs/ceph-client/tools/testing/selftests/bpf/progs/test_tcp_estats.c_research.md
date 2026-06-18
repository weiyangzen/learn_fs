<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_estats.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_estats.c

## Purpose

Verifier-focused TCP event statistics program using mocked socket structures and packed connection IDs. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 257 source lines. BPF sections: `.maps`, `tp/dummy/tracepoint`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_HASH`. Important helper/kfunc surface: `bpf_get_prandom_u32`, `bpf_helpers`, `bpf_ktime_get_ns`, `bpf_map_update_elem`, `bpf_probe_read_kernel`. Important C functions and entry points include `_dummy_tracepoint`. Notable globals or configuration/result fields include `int _dummy_tracepoint(struct dummy_tracepoint_args *arg)`.

## Control Flow

A dummy tracepoint reads a `sock *`, initializes event metadata, extracts IPv4/IPv6 addresses and ports with probe reads, and stores a `tcp_estats_basic_event` in a hash map.

## State And Persistence Behavior

`ev_record_map` stores the generated event keyed by a test key. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Packed struct writes, unaligned address copies, and compiler-generated variable-offset stack patterns are the intended verifier stress points. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

Load-time verifier acceptance and map record shape after dummy tracepoint execution are the main signals. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcp_estats.c -->
