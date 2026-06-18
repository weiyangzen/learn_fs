<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sample_map_ret0.bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sample_map_ret0.bpf.c

## Purpose

`sample_map_ret0.bpf.c` is a tiny XDP eBPF program intended to always load successfully while exercising map-definition and map-lookup verifier/control paths.

## Important APIs, Types, and Functions

It uses libbpf-style `SEC` and BTF map declaration macros from `bpf_helpers.h`. The file declares a hash map `htab` keyed by `__u32` with `long` values and an array map `array` with two entries. The `SEC("xdp") int func()` program calls `bpf_map_lookup_elem` on both maps and returns 0 only if both lookups are non-null.

## Control Flow

The XDP entry initializes zero keys, looks up the hash map, returns 1 on miss, looks up the array map using a 64-bit zero variable passed to a `__u32` key map, returns 1 on miss, and otherwise returns 0. For control-path loading tests, the verifier and loader behavior matter more than packet semantics.

## State and Persistence Behavior

Persistent state is limited to BPF map definitions when the object is loaded. Runtime map contents determine whether the program returns 0 or 1, but the source itself does not populate maps.

## Dependencies and Integration Points

It depends on kernel BPF/XDP support, libbpf helper macros, and build rules that compile `.bpf.c` objects. It is likely used by loader selftests that need a simple program with maps.

## Risks and Edge Cases

The array lookup uses `key64` even though the declared key type is `__u32`; verifier acceptance of the pointer size and BTF metadata is part of the intended coverage. If maps are empty, the hash lookup returns null and the program returns 1, which is acceptable for load-path tests but not a packet-pass program.

## Test Signals

Useful signals are successful BPF object compilation, verifier load success, map creation, and no unexpected verifier rejection around map lookups or section metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sample_map_ret0.bpf.c -->
