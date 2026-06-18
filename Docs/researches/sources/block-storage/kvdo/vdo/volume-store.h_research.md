# File Research: sources/block-storage/kvdo/vdo/volume-store.h

## Purpose
Defines the volume-store abstraction over `dm-bufio` for fixed-size volume pages.

## Public Types
- `struct volume_store`: holds a `struct dm_bufio_client *`.
- `struct volume_page`: holds a `struct dm_buffer *`.

## Public API
- Lifecycle:
  - `open_volume_store()`
  - `close_volume_store()`
  - `initialize_volume_page()`
  - `destroy_volume_page()`
  - `release_volume_page()`
- IO:
  - `read_volume_page()`
  - `prepare_to_write_volume_page()`
  - `write_volume_page()`
  - `sync_volume_store()`
  - `prefetch_volume_pages()`
- Utilities:
  - `get_page_data()`
  - `swap_volume_pages()`

## Dependencies
Includes `common.h`, `compiler.h`, `memory-alloc.h`, and Linux `<linux/dm-bufio.h>`. Forward-declares `struct index_layout`.

## Notes
The abstraction hides bufio details from the volume and page-cache code while keeping page data access cheap through the inline `get_page_data()` helper.
