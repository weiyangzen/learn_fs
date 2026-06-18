# sources/distributed-fs/ceph-client/drivers/gpu/drm/vboxvideo/vbox_hgsmi.c

## Purpose

`vbox_hgsmi.c` implements the low-level HGSMI guest-heap transport: command buffer allocation, checksum generation, buffer free, and host notification through the HGSMI guest I/O port.

## Important APIs, Types, and Functions

- `hgsmi_hash_process`, `hgsmi_hash_end`, and `hgsmi_checksum`: compute the VirtualBox one-at-a-time hash over command offset, header, and tail prefix.
- `hgsmi_buffer_alloc`: allocates header + payload + tail from the guest `gen_pool`, fills header/tail metadata, and returns the payload pointer.
- `hgsmi_buffer_free`: recovers the header from a payload pointer and frees the full allocation.
- `hgsmi_buffer_submit`: converts the header virtual address to a guest physical/VRAM offset, writes it to `VGA_PORT_HGSMI_GUEST`, and executes a memory barrier.

## Control Flow

Higher-level helpers request a payload buffer with a channel and command id. After payload fill, they submit it, allowing the host to process and possibly modify the buffer. They then read response fields and free the allocation.

## State and Persistence Behavior

The gen_pool owns guest-heap allocation state. Individual command buffers are short-lived shared VRAM records. Submission has persistent host-side effects depending on command type. The memory barrier after `outl` tells the compiler/CPU that the host may have modified shared memory.

## Dependencies and Integration Points

It depends on Linux generic allocator DMA APIs, VirtualBox VBE/HGSMI ports, and header/tail definitions. It is the transport for `hgsmi_base.c`, `modesetting.c`, and `vbva_base.c`.

## Risks and Edge Cases

- All callers must submit/free payload pointers returned by this allocator; arbitrary pointers corrupt gen_pool accounting.
- `total_size = size + header + tail` is not overflow-checked.
- Host processing is synchronous from the driver's perspective; if a host delays writes, response reads could be stale.
- Checksum must match host expectations exactly, including the command offset passed into the hash.

## Test Signals

Allocation/free stress in guest heap, checksum verification against known host implementation, command submission smoke tests, and fault injection for exhausted guest heap or invalid pool mappings.
