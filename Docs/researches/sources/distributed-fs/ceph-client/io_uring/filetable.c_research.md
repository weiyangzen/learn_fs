# sources/distributed-fs/ceph-client/io_uring/filetable.c

## Purpose
`filetable.c` manages fixed-file table allocation, installation, removal, and automatic slot allocation for io_uring registered files.

## Important APIs, Types, And Functions
- `io_alloc_file_tables()` allocates resource node storage and the allocation bitmap.
- `io_free_file_tables()` frees resource data and bitmap.
- `__io_fixed_fd_install()` installs a file at a requested 1-based slot or automatically allocated slot.
- `io_fixed_fd_install()` wraps installation with submit locking and drops the file on error.
- `io_fixed_fd_remove()` clears an existing fixed-file slot.
- `io_register_file_alloc_range()` sets the auto-allocation range from userspace.

## Control Flow
Auto allocation uses `io_file_bitmap_get()` to scan from `alloc_hint` within `[file_alloc_start, file_alloc_end)`, wrapping once. Installation rejects io_uring files, missing tables, and out-of-range slots, allocates a resource node, resets any existing node at the slot, sets the bitmap, and stores encoded file pointer/flags. Removal validates the slot, resets the node, and clears the bitmap.

## State And Persistence
Per-ring state lives in `ctx->file_table.data.nodes`, `ctx->file_table.bitmap`, `alloc_hint`, and allocation range fields. Each node stores an encoded file pointer plus NOWAIT/regular-file flags.

## Dependencies And Integration Points
It depends on resource table helpers (`io_rsrc_data_alloc/free`, `io_rsrc_node_alloc/lookup/reset`), filetable inline encoding from `filetable.h`, submit locking, and UAPI `io_uring_file_index_range`.

## Risks And Edge Cases
Slot numbering differs between explicit userspace slots and zero-based internals; `IORING_FILE_INDEX_ALLOC` returns a zero-based allocated slot. Installing io_uring files is rejected to avoid recursion. Bitmap and node updates require `uring_lock` protection. Range overflow is checked with `check_add_overflow()`.

## Test Signals
Registered-file tests should cover explicit slots, auto allocation and wrap, allocation range validation, removal, io_uring file rejection, fixed file replacement, and error cleanup/fput.
