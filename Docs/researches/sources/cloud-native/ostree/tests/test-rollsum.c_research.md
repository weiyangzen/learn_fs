# sources/cloud-native/ostree/tests/test-rollsum.c

## Purpose
This C unit test validates OSTree's rolling checksum matching and bupsplit checksum helper, including collision safety and randomized buffer scenarios.

## Important APIs, Types, And Functions
It uses `_ostree_compute_rollsum_matches()`, `_ostree_rollsum_matches_free()`, `OstreeRollsumMatches`, `bupsplit_find_ofs`, `bupsplit_sum`, `GBytes`, `GVariant` match tuples `(uttt)`, and GLib random/test utilities.

## Control Flow
`test_rollsum_helper()` computes matches for two buffers, checks whether matches are expected, iterates match variants, validates offsets, source/target bounds, byte equality for matched ranges, and `match_size` accounting. `test_rollsum()` checks known CRC32 collision buffers should not match, identical large random buffers should match, modified chunk-boundary buffers should retain matches, duplicated chunks should match, and fully different buffers should not. `test_bupsplit_sum()` checks sums are invariant across window-offset cases.

## State And Persistence
All buffers and match arrays are in memory. No files are written.

## Dependencies And Integration Points
This integrates rollsum, bupsplit chunking, GLib `GBytes`, and bsdiff/bspatch headers included by the test build. It guards static delta diffing and content deduplication internals.

## Risks
CRC collisions must be rejected by byte comparison. Offset and match-size accounting can overflow or point outside buffers if rollsum logic is wrong. Randomized tests may be expensive but cover realistic large data.

## Test Signals
GLib test paths `/rollsum` and `/bupsum` fail on unexpected match counts, invalid offsets, mismatched bytes, or sum invariants.
