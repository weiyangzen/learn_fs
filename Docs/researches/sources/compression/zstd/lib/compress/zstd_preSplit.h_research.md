# sources/compression/zstd/lib/compress/zstd_preSplit.h

## Purpose
`zstd_preSplit.h` exposes the small pre-split API for deciding whether a 128 KiB block should be split before compression.

## Important APIs, Types, And Functions
The header defines `ZSTD_SLIPBLOCK_WORKSPACESIZE` as 8208 bytes and declares `ZSTD_splitBlock(const void* blockStart, size_t blockSize, int level, void* workspace, size_t wkspSize)`.

## Control Flow
There is no header control flow. The documented contract says `level` must be 0 through 4, `workspace` must be `size_t` aligned and large enough, and current implementation expects `blockSize == 128 KB`.

## State And Persistence
No state is owned by the header. The implementation uses only caller-provided workspace and returns the selected split position or the original block size.

## Dependencies And Integration Points
It includes `<stddef.h>` for `size_t` and is implemented by `zstd_preSplit.c`. Higher-level compression code can include it to invoke the pre-split heuristic before normal block compression.

## Risks
The fixed workspace size is an ABI-like contract with the implementation. If the implementation's histogram structs grow beyond this size, callers can corrupt memory. The 128 KiB-only limitation must be respected by all callers.

## Test Signals
Compile coverage plus direct calls at all legal levels are the basic signals. Integration tests should verify callers allocate aligned workspace of at least the advertised size and never pass partial blocks unless the implementation is extended.
