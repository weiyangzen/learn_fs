# File Research: sources/block-storage/linux-dm/drivers/md/bcache/extents.h

## Purpose
Declares bcache btree-key operation tables and external extent/pointer validation and formatting helpers.

## Main Interfaces
- Extern operation tables: `bch_btree_keys_ops` and `bch_extent_keys_ops`.
- Helpers: `bch_extent_to_text()`, `__bch_btree_ptr_invalid()`, and `__bch_extent_invalid()`.

## Integration Points
Included by `btree.c`, `debug.c`, and other bcache code that needs to initialize btree nodes with the correct key operations or print/validate keys.

## Risks And Review Focus
- This header is intentionally minimal; operation-table semantics live in `extents.c`.
- Callers must choose the correct ops table for interior versus leaf nodes.
