# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_lmtt_ml.c

## Purpose
`xe_lmtt_ml.c` implements the multi-level LMTT variant for newer platforms with 48-bit local-memory host and guest address width.

## Important APIs, Types, And Functions
- Exports `const struct xe_lmtt_ops lmtt_ml_ops`.
- Root level is 2, intermediate level is 1, leaf level is 0.
- PDEs are 64-bit, leaf PTEs are 32-bit.
- Level-1 spans 32 GiB chunks; leaf entries map 2 MiB pages.
- Encoding validates 64 KiB directory-pointer alignment and 2 MiB LMEM page alignment.

## Control Flow
The common LMTT manager recurses through levels 2 and 1 using this ops table, then writes level-0 PTEs for VRAM backstore. Indexing uses guest address bits shifted by either 35 or 21 bits depending on level.

## State And Persistence
The file owns no mutable state. It supplies static ops used to encode persistent table BO contents.

## Dependencies And Integration Points
It integrates with `xe_lmtt.c` via `struct xe_lmtt_ops` and relies on bitfield/log2/sizes helpers plus `XE_WARN_ON()`.

## Risks
48-bit field fitting is easy to break if hardware field definitions change. Level numbering is implementation-specific and must remain consistent with common recursive allocation. Alignment violations warn rather than fail.

## Test Signals
Verify root/intermediate/leaf entry counts, level shifts, index calculations across 32 GiB boundaries, and PTE/PDE field encoding for high offsets up to 48-bit limits.
