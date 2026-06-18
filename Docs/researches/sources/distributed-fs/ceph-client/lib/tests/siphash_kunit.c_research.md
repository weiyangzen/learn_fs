## sources/distributed-fs/ceph-client/lib/tests/siphash_kunit.c

### Purpose
This KUnit suite verifies the kernel SipHash and HalfSipHash implementations against known reference vectors. It covers aligned and intentionally unaligned byte input plus specialized integer helper entry points.

### Important APIs, types, and functions
Static keys `test_key_siphash` and `test_key_hsiphash` are fixed byte-order test keys. `test_vectors_siphash[64]` contains SipHash2-4 reference outputs. `test_vectors_hsiphash[64]` is selected differently for 64-bit and 32-bit `BITS_PER_LONG`, matching architecture-dependent HalfSipHash key shape. The `chk()` macro wraps `KUNIT_EXPECT_EQ_MSG()`. `siphash_test()` exercises `siphash()`, `hsiphash()`, `siphash_1u64()` through `siphash_4u64()`, `siphash_1u32()` through `siphash_4u32()`, and halfsiphash u32 helpers.

### Control flow
The single test case initializes aligned arrays `in[64]` and `in_unaligned[65]`, fills incremental byte values, and for lengths 0 through 63 compares aligned and `+1` unaligned hash results against the corresponding vector. It then checks specialized integer helper calls by composing integer values whose byte representation corresponds to selected vector lengths.

### State and persistence
All input buffers are stack-local and deterministic. Static key/vector tables are immutable. No persistent state, randomization, or allocation is involved.

### Dependencies and integration points
The suite depends on KUnit, `linux/siphash.h`, kernel type/bitness definitions, and module metadata. It registers as suite `siphash` and is dual-licensed BSD/GPL consistent with the implementation lineage.

### Risks and edge cases
HalfSipHash expected vectors differ by word size, so architecture-specific branches must stay synchronized with implementation behavior. The test validates known vectors and unaligned access but does not benchmark performance or test randomized keys beyond the fixed reference key. Endianness assumptions are encoded in the chosen constants and helper expectations.

### Test signals
Strong signals are 64 reference lengths for SipHash and HalfSipHash, aligned versus unaligned equality to the same vectors, architecture-specific HalfSipHash vector coverage, and coverage of optimized fixed-width integer helper APIs.
