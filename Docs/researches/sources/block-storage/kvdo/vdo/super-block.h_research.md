# File Research: sources/block-storage/kvdo/vdo/super-block.h

This header declares the opaque `struct vdo_super_block` API. It exposes free, asynchronous save, asynchronous load, and codec accessor functions.

The save/load APIs take physical block offsets and parent `vdo_completion` objects, reflecting that the super block is managed as VDO metadata I/O rather than synchronous direct buffer access.
