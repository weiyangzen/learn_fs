# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_preSplit.c

## Purpose

`zstd_preSplit.c` implements a heuristic for pre-splitting full 128 KiB blocks when the beginning and end of a block appear statistically different. The split point can improve compression when a block contains two different data distributions by allowing later compression stages to process more homogeneous pieces.

## Important APIs, Types, and Functions

The single public function is `ZSTD_splitBlock()`. Internal data structures are `Fingerprint`, which stores event counts and a total event count, and `FPStats`, which holds past and new fingerprints. `hash2()` hashes one or two bytes depending on hash-table size. `recordFingerprint_generic()` and generated `ZSTD_recordFingerprint_*()` functions sample events at different rates. `fpDistance()` computes a normalized absolute difference between fingerprints, and `compareFingerprints()` checks that distance against a threshold. `ZSTD_splitBlock_byChunks()` scans 8 KiB chunks, while `ZSTD_splitBlock_fromBorders()` performs the cheaper border/middle heuristic.

## Control Flow

`ZSTD_splitBlock()` accepts a level from 0 to 4. Level 0 calls `ZSTD_splitBlock_fromBorders()`. That path records byte histograms for the first and last 512 bytes, returns no split if they are not sufficiently different, then samples the middle 512 bytes and chooses 32 KiB, 64 KiB, or 96 KiB based on which side the middle resembles. Levels 1 through 4 call `ZSTD_splitBlock_byChunks()` with increasingly dense sampling. The chunk path records the first 8 KiB as the reference, then compares each subsequent 8 KiB chunk to accumulated past events. If the new chunk differs enough, its offset is returned as the split point; otherwise events are merged and the penalty threshold is gradually relaxed.

## State and Persistence Behavior

All state is temporary and stored in caller-provided workspace. The functions assert that the workspace is aligned and large enough for `FPStats`. `ZSTD_splitBlock_fromBorders()` also uses an additional `Fingerprint` carved out of the same workspace at `512 * sizeof(unsigned)`. No persistent compressor state is modified.

## Dependencies and Integration Points

The file includes common compiler, memory, dependency, and internal headers, plus `hist.h` and `zstd_preSplit.h`. It depends on `HIST_add()` for byte histograms in the fast border mode and uses `ZSTD_SLIPBLOCK_WORKSPACESIZE` from the header to assert workspace capacity. The intended caller is a higher-level compressor path that can split only full 128 KiB blocks.

## Risks

The function currently asserts `blockSize == 128 KiB`; using it on smaller blocks is outside contract. `addEvents_generic()` assumes `srcSize >= HASHLENGTH`; callers satisfy this through fixed chunk sizes. The workspace overlay for `middleEvents` depends on `ZSTD_SLIPBLOCK_WORKSPACESIZE` being large enough and on alignment. The heuristic can choose suboptimal split points because it uses sampled fingerprints rather than full compression estimates. `flushEvents()` and `removeEvents()` are unused, which is intentional but can confuse maintainers.

## Test Signals

Tests should cover level 0 through 4 on 128 KiB synthetic blocks: uniform data should return `blockSize`, sharply different halves should split near the transition, and border/middle cases should produce 32 KiB, 64 KiB, or 96 KiB as designed. Debug builds should assert on invalid level, undersized workspace, and non-128 KiB blocks. Compression integration tests should verify that a returned split still round-trips after both pieces are compressed.
