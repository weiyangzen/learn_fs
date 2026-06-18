# sources/distributed-fs/ceph-client/lib/raid/xor/tests/xor_kunit.c

Purpose: unit-tests the exported `xor_gen()` API against a bytewise reference implementation.

Important APIs and flow: fixed seed `XOR_KUNIT_SEED` makes randomized tests repeatable. Suite init allocates guard-page-backed `vmalloc()` buffers, fills destination/reference/source data, then `xor_test()` runs 1000 iterations with random source counts up to 64, 512-byte-multiple lengths up to 16 KiB, random 64-byte alignments, and end-of-buffer placements. It compares `xor_ref()` and `xor_gen()` with `KUNIT_EXPECT_MEMEQ_MSG()`.

State and persistence: module-global buffers and PRNG state live for the suite and are released in `xor_suite_exit()`. No persistent state.

Dependencies and integration: depends on KUnit, `prandom`, `vmalloc`, `linux/raid/xor.h`, and the selected XOR implementation behind `xor_gen()`.

Risks and test signals: this is the primary regression signal for generic and architecture XOR routines, especially buffer overreads and multi-source dispatch. It does not exhaustively test every CPU feature path unless run on those architectures/configurations.
