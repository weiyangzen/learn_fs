<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_ptr_arith.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_ptr_arith.c

## Purpose
This large verifier suite exercises arithmetic on map value pointers across constant and unknown scalar offsets, different maps with compatible/incompatible value shapes, lower and upper out-of-bounds cases, scalar/pointer state merging, and 32-bit packet pointer arithmetic.

## Important APIs, Types, and Functions
It declares `map_array_48b`, `map_hash_16b`, and `map_hash_48b` with different map types and value sizes. Programs use `bpf_map_lookup_elem`, `bpf_map_delete_elem`, `bpf_get_prandom_u32`, `errno` constants, and `__sk_buff` offsets for skb length and packet data/data_end.

## Control Flow
Early programs choose between maps based on skb length, load a value pointer, derive either constant or unknown scalar offsets from map content or random data, and add those offsets to the pointer. They test whether verifier can prove equal offsets or compatible map value properties across branches. Middle programs mix pointer and scalar alternatives through a common ALU instruction to verify unprivileged sanitization and nospec insertion. Further cases probe upper and lower out-of-bounds arithmetic, legal known offsets, known and unknown scalar additions/subtractions, pointer-plus-pointer and scalar-minus-pointer rejections, tainted destination leakage, and 32-bit ALU on packet pointers.

## State and Persistence
The maps are fixtures for pointer provenance and value-size information. Some tests write values, but the durable artifact is verifier state: pointer min/max bounds, map ID, fixed/variable offset, scalar range, and speculative-execution sanitization.

## Dependencies and Integration Points
This file is loaded by the verifier selftest framework as socket and tc programs. It depends on precise map BTF/type declarations, `bpf_misc.h` annotations, and `SPEC_V1`-conditioned translated instruction checks for nospec placement.

## Risks
The suite is sensitive to verifier range analysis improvements, especially when different maps share value layout. Error text for unprivileged arithmetic and out-of-range conditions is also brittle. Inline assembly sequences intentionally preserve specific branch shapes.

## Test Signals
Success on provably safe pointer+scalar cases, failure on negative minimum offsets, max outside value bounds, pointer-pointer arithmetic, and unprivileged mixed pointer/scalar arithmetic are the key signals. `__retval` checks validate accepted execution paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_value_ptr_arith.c -->
