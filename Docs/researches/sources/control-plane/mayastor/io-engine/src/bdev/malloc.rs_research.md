<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/malloc.rs -->
# sources/control-plane/mayastor/io-engine/src/bdev/malloc.rs

Purpose: URI-backed implementation for SPDK malloc bdevs allocated from hugepage memory.

Important APIs/types: `Malloc` stores name, alias, block count, block size, optional UUID, and resize flag. `TryFrom<&Url>` parses `blk_size`, `size_mb`, `size`, `num_blocks`, `uuid`, and `resize`; validates block size is 512 or 4096; enforces exactly one size source. `Probe` rejects import mode because malloc devices are volatile. `create()` creates a malloc disk with `create_malloc_disk`, sets UUID/alias, or resizes an existing bdev when `resize` is present. `destroy()` asynchronously calls `delete_malloc_disk`. `try_resize()` calls `resize_malloc_disk`.

State and dependencies: mutates SPDK bdev registry and consumes hugepage memory. Depends on byte-unit parsing, SPDK malloc APIs, and callback oneshots for delete.

Risks and test signals: resize converts target size to whole MiB, losing sub-MiB precision. Missing hugepages surface as create failures. Test parameter validation, UUID aliasing, duplicate create versus resize, and cleanup after destroy.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bdev/malloc.rs -->
