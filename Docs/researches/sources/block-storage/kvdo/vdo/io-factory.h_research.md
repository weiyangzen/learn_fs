# File Research: sources/block-storage/kvdo/vdo/io-factory.h

Public interface for UDS index storage access.

Key responsibilities:
- Declares opaque `struct io_factory`.
- Defines `UDS_BLOCK_SIZE` as 4096 bytes.
- Declares factory lifecycle, backing-store replacement, refcount operations, writable-size query, dm-bufio creation, and buffered reader/writer creation.

Dependencies:
- Includes buffered reader/writer APIs and Linux dm-bufio.

Notable risks:
- Documentation mentions block device or file, but the implementation in this tree is block-device oriented.
- Header notes remaining hardcoded 4K constants should be converted to `UDS_BLOCK_SIZE`.
