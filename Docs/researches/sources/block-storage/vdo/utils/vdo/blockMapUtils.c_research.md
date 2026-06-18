# File Research: sources/block-storage/vdo/utils/vdo/blockMapUtils.c

Implements user-space traversal and lookup helpers for the VDO block map.

Key details:
- `examineBlockMapEntries()` walks every block-map tree root and recursively visits mapped child pages.
- `readAndExaminePage()` reads a block-map page, validates it, calls the supplied `MappingExaminer` for every entry, and descends into valid data-block PBNs when height remains.
- `findLBNPage()` computes tree slots for a logical block number and walks from the relevant root page to the leaf page.
- `findLBNMapping()` resolves a single LBN to a mapped PBN and mapping state, returning the zero block with `UNMAPPED` state for missing mappings.
- `readBlockMapPage()` validates page version, nonce, initialized bit, and expected PBN; invalid or wrong-location pages are treated as uninitialized after warning.

Risk notes:
- Traversal calls the examiner before checking whether a location is mapped, so examiners must handle unmapped entries.
- Invalid pages are softened into uninitialized pages, which is useful for diagnostic tools but can hide metadata damage unless warnings are monitored.
