
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/hash_large_key.c

## Purpose

`hash_large_key.c` verifies BPF hash map behavior with a large key structure around 4 KiB and BPF-side map access that changes an associated value.

## Important APIs, Types, and Functions

The harness uses `test_hash_large_key.skel.h`, obtains `hash_map` FD, attaches raw tracepoint programs, and calls `bpf_map_update_elem()`/`bpf_map_lookup_elem()` with a `struct bigelement` key.

## Control Flow and Data Flow

It loads and attaches the skeleton, inserts key `{0}` with value 21, mutates only `key.c` to 1, then looks up the value and expects 42, indicating the BPF-side program populated/used the large key path.

## State, Dependencies, Integration Points, Risks, and Test Signals

State is one hash map with large keys and skeleton links. Dependencies include hash map large-key support and the paired BPF program's tracepoint trigger. Integration is kernel hashing/copying of large keys. Risks are stack/heap key layout mismatch and paired BPF object assumptions. Test signal is successful lookup with value 42 for the mutated large key.
