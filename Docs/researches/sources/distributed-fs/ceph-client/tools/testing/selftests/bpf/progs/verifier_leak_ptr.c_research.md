# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_leak_ptr.c

## Purpose

`verifier_leak_ptr.c` tests pointer leak prevention to contexts and map values. It distinguishes privileged verifier behavior from unprivileged restrictions and checks atomic stores, direct ctx writes, and map-value writes involving pointer-typed registers.

## Important APIs, Types, and Functions

The file declares `map_hash_8b` and four socket programs. Test cases attempt to store pointer values into ctx memory or map value memory. Metadata records privileged failures for atomic ctx stores and unprivileged failures such as `R2 leaks addr into mem`, `R10 leaks addr into mem`, `R2 leaks addr into ctx`, and `R6 leaks addr into mem`.

## Control Flow

The first two tests use BPF atomic store forms targeting ctx memory, which are rejected in privileged mode and additionally flagged as pointer leaks in unprivileged mode. The third writes a pointer into ctx through a non-atomic path that privileged mode accepts but unprivileged mode rejects. The final test obtains a map value and writes a pointer into it, again permitted only in privileged mode by the declared expectations.

## State and Persistence Behavior

Persistent state is the hash map. Runtime state includes pointer-valued registers such as stack/frame pointers or map-value pointers. The verifier must prevent unprivileged programs from materializing kernel addresses in memory visible after execution.

## Dependencies and Integration Points

The file integrates with unprivileged verifier policy, pointer leak checks, atomic store validation, ctx write permissions, and map-value access rules.

## Risks and Test Signals

Risks are kernel address disclosure to unprivileged BPF, over-restricting privileged programs, or allowing atomic ctx stores. Test signals are the declared privileged and unprivileged outcomes and exact leak diagnostics for memory, ctx, and map-value destinations.
