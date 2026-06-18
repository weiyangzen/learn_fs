# sources/distributed-fs/orangefs/src/common/misc/mmap-ra-cache.h

Purpose: Defines the public data structures, defaults, status codes, and function prototypes for the mmap readahead cache. It is the contract between client-core I/O code and `mmap-ra-cache.c`.

Important APIs and types: Default and maximum tunables include buffer size/count, read count, and pinned-memory setting. Status constants distinguish no cache, valid hit, wait-on-fill, need-read, and posted-read states. `gen_link_t` wraps queued VFS request payloads. `racache_file_t` indexes cached buffers by `PVFS_object_ref` and per-file read count. `racache_buffer_t` holds list links, validity/free/resize flags, buffer id, waiter count, file offset, data size, buffer size, read count, raw buffer pointer, and owning file. `racache_t` is the singleton cache state with mutex, tunables, free/LRU lists, quickhash table, active buffer array, and old resize array.

Control flow and integration: Consumers initialize the cache, tune counts/sizes/read-ahead/pinning, call `pint_racache_get_block()` before normal I/O, fill returned buffers when `RACACHE_READ` is returned, call `pint_racache_make_free()` when buffers are reusable, flush per file, and finalize on shutdown. `pint_racache_buff_offset()` standardizes cache-line alignment for file offsets.

State and persistence behavior: The header exposes mutable state types but does not define the singleton. All state is volatile process memory and is meant to optimize reads rather than persist correctness data. The wait-list fields make buffer lifetime depend on external request completion.

Dependencies and risks: Depends on quickhash, PVFS internal types, and quicklist-compatible list links. External callers can see internal structures, so invariants such as list membership, `valid`, `vfs_cnt`, `being_freed`, and `resizing` must be honored by all users. Test signals include compile compatibility with client-core call sites and ABI-level validation that status codes are interpreted consistently.
