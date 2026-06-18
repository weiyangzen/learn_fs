# sources/distributed-fs/beegfs/common/tests/TestStripePattern.cpp

Purpose: This parameterized test validates basic `Raid0Pattern` chunk mapping semantics for different chunk sizes.

Important APIs/types/functions: `Raid0PatternTest` derives from `testing::TestWithParam<unsigned>`. The test instantiates chunk sizes of `64*1024` and `1024*1024*1024`, then constructs `Raid0Pattern` with target sequence `{0,1,2,3}`.

Control flow: For ten full rotations across the target list, it computes each chunk's start and end offset. It asserts that `getStripeTargetIndex()` returns `i % targetPattern.size()` at both boundaries and that `getChunkStart()` returns the chunk's starting offset for both start and last-byte positions.

State and persistence behavior: No state is persisted. The test protects striping math used to map logical file offsets to storage targets and chunk starts.

Dependencies and integration: `Raid0Pattern` is used by metadata creation paths and serialized striping pattern state. Correct chunk math is critical for read/write routing and file layout consistency.

Risks and test signals: It covers boundary positions and very large chunk sizes but not negative offsets, overflow near `int64_t` limits, empty target vectors, default target counts, serialization, or other striping subclasses. It is a focused arithmetic regression test.
