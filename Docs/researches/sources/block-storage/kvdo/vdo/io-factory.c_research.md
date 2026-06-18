# File Research: sources/block-storage/kvdo/vdo/io-factory.c

Kernel block-device I/O factory for UDS index storage and dm-bufio region access.

Key responsibilities:
- Opens block devices by `major:minor` string or path.
- Abstracts kernel API differences across upstream/RHEL versions with `blkdev_get_*`, `bdev_open_*`, or `bdev_file_open_*`.
- Reference-counts `struct io_factory` instances.
- Replaces the backing storage for an existing factory.
- Reports writable size via block-device inode size.
- Creates dm-bufio clients for aligned regions.
- Opens UDS buffered readers/writers over 4K-block regions.

Important behavior:
- Requires read/write block-device open mode.
- `make_uds_io_factory()` returns the factory with refcount 1.
- `put_uds_io_factory()` closes/releases the backing handle when refcount reaches zero.
- `make_uds_bufio()` validates sector-aligned offsets and block sizes that are multiples of `UDS_BLOCK_SIZE`.
- Buffered reader/writer helpers require region size to be a multiple of `UDS_BLOCK_SIZE` and reserve one dm-bufio buffer.

Dependencies:
- Linux block-device, mount, version, dm-bufio APIs; UDS logging and memory allocation.

Notable risks:
- Conditional API compatibility branches are complex and version-sensitive.
- `replace_uds_storage()` swaps the backing device without explicit synchronization; callers must ensure no unsafe concurrent users.
- The `new_layout` parameter to `create_layout_factory()` in `index-layout.c` is unused by this layer.
