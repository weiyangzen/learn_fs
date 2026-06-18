<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpnotify_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpnotify_kern.c

## Purpose

Sockops notification test that emits perf events on TCP retransmit and state callbacks. This file is part of Linux `tools/testing/selftests/bpf/progs` and is used as a BPF-side fixture rather than production Ceph client code.

## Important APIs, Types, And Data

The object has 92 source lines. BPF sections: `.maps`, `.maps`, `sockops`, `license`. Map types declared or referenced: `BPF_MAP_TYPE_ARRAY`, `BPF_MAP_TYPE_PERF_EVENT_ARRAY`. Important helper/kfunc surface: `bpf_endian`, `bpf_helpers`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_ntohl`, `bpf_perf_event_output`, `bpf_sock_ops`, `bpf_sock_ops_cb_flags_set`, `bpf_testcb`. Important C functions and entry points include `bpf_testcb`. Notable globals or configuration/result fields include `int bpf_testcb(struct bpf_sock_ops *skops)`.

## Control Flow

The program initializes sockops callback flags, updates `global_map`, and writes structured records to `perf_event_map` with `bpf_perf_event_output`.

## State And Persistence Behavior

`global_map` stores counters and last observed fields; `perf_event_map` streams user-visible events. Map entries, globals in `.data`/`.bss`/`.rodata`, attached links, and referenced kernel objects live across individual program invocations until the user-space selftest tears down the skeleton.

## Dependencies And Integration Points

It is compiled by the selftests BPF build into a libbpf skeleton object, loaded by the matching user-space selftest, and depends on kernel BPF verifier, helper, attach-type, and BTF/CO-RE behavior matching the section and type annotations in the source. Integration is with libbpf section parsing, generated skeleton accessors, the matching selftest driver, and kernel subsystems implied by the section names and helpers listed above.

## Risks And Edge Cases

Perf-event record layout and callback flag setup must match user-space reader expectations. Changes in compiler code generation, BTF type layout, helper allow-lists, or expected attach type can turn these files into verifier failures even when source-level behavior appears unchanged.

## Test Signals

The harness should observe expected perf records and global counters during TCP activity. Useful additional signals are successful object build, verifier logs matching expected accept/fail annotations, and non-empty or expected-valued result maps/globals after the user-space harness runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/test_tcpnotify_kern.c -->
