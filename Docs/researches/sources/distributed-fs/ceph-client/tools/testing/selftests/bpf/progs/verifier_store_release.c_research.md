# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_store_release.c

## Purpose
`verifier_store_release.c` tests verifier support for atomic store-release instructions. It validates legal stack store-release widths, operand initialization checks, destination pointer classes, alignment, pointer leakage through store-release, invalid register encoding, and fallback behavior when atomics support is unavailable.

## Important APIs, Types, and Functions
The file uses low-level BPF instruction encoding from `../../../include/linux/filter.h` and inline assembly. It declares `map_hash_8b` for a map-value pointer leakage test and calls `bpf_map_lookup_elem`. Program types include `socket`, `xdp`, `flow_dissector`, and `sk_reuseport`. An `ENABLE_ATOMICS_TESTS`/toolchain support path emits real tests; otherwise a dummy successful socket program is used.

## Control Flow
Valid stack tests perform 8-, 16-, 32-, and 64-bit store-release operations and return zero. Negative tests omit source or destination initialization, use a scalar destination, use misaligned stack destination, attempt atomic stores into ctx, packet, flow_keys, or sock pointers, or encode invalid register `R15`. Pointer leakage tests store stack and map pointers with release semantics and distinguish privileged success from unprivileged pointer-leak rejection.

## State and Persistence
The only persistent object is the hash map used to obtain a map-value pointer. Otherwise state is stack/register verifier metadata and pointer-type provenance. Store-release itself is a memory-ordering operation but these fixtures do not coordinate with concurrent runtime state.

## Dependencies and Integration Points
The source depends on Clang/JIT atomics support, BPF atomic instruction encoding, verifier memory-class rules, and unprivileged pointer leak policy. It integrates with the selftest runner through exact messages such as `R2 !read_ok`, `BPF_ATOMIC stores into R1 ctx is not allowed`, and `R6 leaks addr into map`.

## Risks and Test Signals
Risks include accepting store-release to read-only or unsafe pointer classes, missing alignment enforcement, failing to detect uninitialized operands, or mishandling pointer leaks via atomics. Test signals are width-specific success cases, deterministic failures for invalid pointer classes and registers, and a dummy success path that prevents unsupported environments from failing unrelated test runs.
