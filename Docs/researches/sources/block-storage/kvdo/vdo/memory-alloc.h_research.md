# File Research: sources/block-storage/kvdo/vdo/memory-alloc.h

## Purpose
Declares the UDS allocation API and provides typed allocation macros used throughout the VDO/UDS code.

## Key API / Macros
- `uds_allocate_memory`, `uds_free_memory`, `uds_reallocate_memory`, `uds_duplicate_string`.
- `UDS_ALLOCATE`: typed zeroed allocation.
- `UDS_ALLOCATE_EXTENDED`: allocates a primary struct plus trailing array storage.
- `UDS_ALLOCATE_IO_ALIGNED`: page-aligned allocation for I/O buffers.
- `uds_allocate_cache_aligned`: cache-line-aligned allocation helper.
- `UDS_FORGET`: NULLs a pointer and returns its previous value for ownership transfer.
- `UDS_FREE`: wrapper around `uds_free_memory`.
- `uds_register_allocating_thread` / `uds_unregister_allocating_thread`.
- `get_uds_memory_stats` / `report_uds_memory_usage`.

## Safety Notes
`uds_do_allocation` checks multiplication overflow and intentionally forces an impossible allocation size on overflow so callers get an out-of-memory style failure. `UDS_ALLOCATE_EXTENDED` uses `STATIC_ASSERT` to enforce compatible alignment between the header type and trailing element type.

## Integration Notes
This header is the central memory management interface. It pulls in compiler helpers, CPU cache-line size, assertions, type definitions, page size, and thread registry support.
