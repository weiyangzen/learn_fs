# File Research: sources/block-storage/kvdo/vdo/volume-store.c

## Purpose
Implements the volume backing-store adapter on top of Linux `dm-bufio`. It opens/closes storage, reads pages, prepares writable buffers, marks writes dirty, syncs dirty buffers, and manages page-buffer references.

## Main Functions
- `close_volume_store()`: destroys the `dm_bufio_client` and clears the pointer.
- `initialize_volume_page()`: initializes a `volume_page` by setting its buffer pointer to `NULL`.
- `destroy_volume_page()`: releases any referenced buffer.
- `open_volume_store()`: opens a bufio client through `open_uds_volume_bufio()`.
- `prefetch_volume_pages()`: calls `dm_bufio_prefetch()`.
- `prepare_to_write_volume_page()`: releases any prior page buffer, obtains a new writable bufio buffer with `dm_bufio_new()`, and stores it in the page.
- `read_volume_page()`: releases prior page buffer, reads with `dm_bufio_read()`, stores the returned buffer, and logs read failures.
- `release_volume_page()`: releases a held `dm_buffer` and clears the pointer.
- `swap_volume_pages()`: swaps two `volume_page` structs by value.
- `sync_volume_store()`: writes dirty buffers with `dm_bufio_write_dirty_buffers()` and logs sync errors.
- `write_volume_page()`: marks the current buffer dirty.

## Dependencies
Includes `geometry.h`, `index-layout.h`, `logger.h`, and `volume-store.h`. The header brings in `dm-bufio`.

## Implementation Notes
The `volume_page` object is a reference holder for a `dm_buffer`, not an owned memory allocation. Data access is via `dm_bufio_get_block_data()` from the header’s `get_page_data()` helper.

`write_volume_page()` ignores the `physical_page` argument because the bufio buffer already identifies the block; it only marks the buffer dirty.

## Invariants and Risks
- Callers must release or destroy pages to drop bufio references.
- `prepare_to_write_volume_page()` and `read_volume_page()` both release previous page state before replacing it.
- `sync_volume_store()` converts the bufio return convention by negating `dm_bufio_write_dirty_buffers()` result.
