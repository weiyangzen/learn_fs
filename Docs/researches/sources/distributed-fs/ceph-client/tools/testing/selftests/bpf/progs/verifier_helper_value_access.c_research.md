# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_value_access.c

## Purpose

`verifier_helper_value_access.c` tests helper access to map values with fixed, adjusted, and variable offsets and sizes. It verifies range proofs for full, partial, empty, out-of-bounds, negative, and signed/unsigned comparison cases, plus map helper read/write size validation.

## Important APIs, Types, and Functions

Maps include `map_hash_16b`, `map_hash_48b`, and `map_hash_8b`. The 45 tracepoint programs use helper calls such as `bpf_trace_printk` and map lookup/update helpers through inline assembly. Diagnostics cover invalid zero-sized reads, map-value bounds, negative minimum values, unbounded memory access, and wrong value sizes.

## Control Flow

The first group passes map-value pointers and sizes directly to helpers, varying range width and lower bound. The second and third groups adjust the pointer by constants or constant registers before helper access. The variable group adjusts by a runtime value and uses max/min checks to prove or fail safety. Later tests compare `<`, `<=`, signed `<`, and signed `<=` proof quality, then exercise map lookup/update helper arguments and adjusted map pointers with 16-byte values.

## State and Persistence Behavior

Persistent state is the three hash maps. Runtime state is verifier-only: map-value pointer base, fixed offset, variable offset, size ranges, signedness proofs, and whether a helper reads from or writes to map value memory.

## Dependencies and Integration Points

The file integrates with map helper prototypes, generic helper memory validators, and scalar range analysis. It complements variable-length stack tests by focusing on map-value boundaries.

## Risks and Test Signals

Risks are accepting reads/writes beyond a map value, treating possibly empty reads as safe, losing signed range information, or rejecting safe adjusted pointers. Test signals are successes for bounded full/partial accesses and failures for zero-sized invalid reads, negative ranges, unbounded memory, and wrong helper value sizes.
