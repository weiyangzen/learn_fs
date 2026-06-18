# File Research: sources/block-storage/parted/libparted/fs/r/hfs/cache.c

Custom extent cache for HFS/HFS+ relocation code.

Key behavior:
- `hfsc_new_cache()` creates an indexed linked-reference table plus one or more extent allocation tables.
- Avoids integer overflow when computing linked-reference table size.
- `hfsc_cache_add_extent()` rejects duplicate start blocks, appends storage tables as needed, records extent metadata, and updates required copy-buffer size.
- `hfsc_cache_search_extent()` looks up an extent by start block.
- `hfsc_cache_move_extent()` relocates a cached extent from one start block index to another and rejects duplicate destinations.
- `hfsc_delete_cache()` frees all table blocks and index references.

Important dependencies:
- Cache structures and constants from `cache.h`.
- Libparted exceptions for duplicate extent errors.

Role:
- Tracks extents by allocation-block start for relocation metadata updates.
