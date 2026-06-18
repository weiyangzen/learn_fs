# File Research: sources/block-storage/vdo/utils/vdo/physicalLayer.h

Defines the abstract synchronous block I/O interface used by VDO userspace tools.

Key details:
- `PhysicalLayer` is a vtable-style struct with destroy, block-count, buffer allocation, reader, and writer callbacks.
- Readers and writers operate in VDO block units using `physical_block_number_t` and block count.
- Buffer allocator exists so implementations can provide direct-I/O-compatible buffers.

Research relevance:
- This abstraction lets metadata logic operate over regular files, block devices, read-only files, or offset layers without knowing the backend.
