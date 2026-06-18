# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_preSplit.h

## Purpose

`zstd_preSplit.h` declares the block pre-splitting helper and its workspace size. It documents that the helper is currently restricted to full 128 KiB blocks and provides the single internal entry point used by compression code that wants a cheap split heuristic.

## Important APIs, Types, and Functions

`ZSTD_SLIPBLOCK_WORKSPACESIZE` is defined as `8208`, large enough for the fingerprint workspace used by `zstd_preSplit.c`. `ZSTD_splitBlock()` takes a block pointer, block size, heuristic level, workspace pointer, and workspace size, and returns either a split offset or `blockSize` when no split is advised.

## Control Flow

The header does not implement control flow. Its comments define the caller contract: level must be 0 through 4, higher levels spend more effort on boundary detection, the workspace must be aligned for `size_t`, `wkspSize` must be at least `ZSTD_SLIPBLOCK_WORKSPACESIZE`, and `blockSize` must currently be exactly 128 KiB.

## State and Persistence Behavior

The API is stateless from the caller's perspective aside from temporary writes into the provided workspace. No compression tables, windows, or sequence stores are passed to the function.

## Dependencies and Integration Points

The header includes `<linux/types.h>` for `size_t`. It is implemented by `zstd_preSplit.c` and is intended for higher-level block compression logic that can split 128 KiB blocks before entropy or sequence compression. The naming of `ZSTD_SLIPBLOCK_WORKSPACESIZE` appears to use "SLIP" rather than "SPLIT"; consumers must use the exact macro name.

## Risks

The main risk is contract misuse. Passing smaller blocks, unaligned workspace, or a too-small workspace will trigger assertions in debug builds and may be unsafe in non-debug contexts. The fixed workspace macro must remain synchronized with the implementation's layout assumptions.

## Test Signals

Compile tests should include this header in kernel mode and verify the signature matches `zstd_preSplit.c`. Runtime tests should allocate exactly `ZSTD_SLIPBLOCK_WORKSPACESIZE`, pass aligned storage, and validate all heuristic levels on full 128 KiB blocks.
