# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_helper_access_var_len.c

## Purpose

`verifier_helper_access_var_len.c` verifies helper argument checking for variable-length memory accesses. It covers stack memory, map values, adjusted map pointers, nullable memory pointers, zero-sized accesses, ring-buffer output, and leak prevention for uninitialized stack bytes.

## Important APIs, Types, and Functions

Maps include `map_hash_48b`, `map_hash_8b`, and `map_ringbuf`. Programs attach to tracepoint, tc, and socket sections. Most tests call helpers that read or write memory via pointer-and-size arguments; the explicit helper call visible in C is `bpf_ringbuf_output`. Metadata captures failures for invalid stack reads/writes, negative sizes, zero-sized invalid reads, unbounded memory, scalar pointer misuse, and map-value bounds.

## Control Flow

The stack tests derive sizes with bitwise AND, unsigned comparisons, signed comparisons, and offset additions, then pass stack pointers to helpers. Map tests repeat the same proof patterns with map-value pointers and adjusted offsets. Nullable pointer tests prove that size zero is allowed with null or non-null pointers, while size greater than zero requires a valid memory pointer. Later tests check that helpers cannot leak uninitialized stack memory and that ring-buffer output applies the same variable-length rules.

## State and Persistence Behavior

Persistent state is the three maps. Runtime verifier state tracks stack slot initialization, pointer base and offset, variable size minimum/maximum, nullable pointer refinement, and whether helper access is read or write.

## Dependencies and Integration Points

The file integrates with helper argument descriptors such as memory, memory-or-null, fixed/variable size, and ringbuf output. It depends on map lookup semantics and stack initialization tracking.

## Risks and Test Signals

Risks are unbounded helper memory reads, uninitialized stack leakage, rejecting valid zero-sized nullable operations, or accepting negative or too-large variable sizes. Test signals are accepted bounded stack/map/ringbuf cases and exact failures for invalid stack access, negative min value, scalar expected stack pointer, map bounds, and unbounded memory.
