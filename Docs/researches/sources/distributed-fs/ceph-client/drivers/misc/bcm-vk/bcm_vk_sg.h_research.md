# sources/distributed-fs/ceph-client/drivers/misc/bcm-vk/bcm_vk_sg.h

## Purpose
`bcm_vk_sg.h` declares the VK scatter-gather DMA descriptor format and public allocation/free APIs used by transfer-buffer messages.

## Important APIs, Types, and Functions
`struct bcm_vk_dma` records pinned user pages, coherent SGL memory, DMA handle, SGL length, and direction. `struct _vk_data` is the packed message payload item containing a byte size and 64-bit address. The exported declarations are `bcm_vk_sg_alloc()` and `bcm_vk_sg_free()`. SGL constants describe the firmware list header: number of SG entries, total size, and first `_vk_data` entry offset.

## Control Flow
Message code passes an array of `_vk_data` items and matching `bcm_vk_dma` slots to `bcm_vk_sg_alloc()`. On success the `_vk_data` array has been rewritten from user buffers to firmware-visible SGL descriptors; later `bcm_vk_sg_free()` releases all populated DMA slots.

## State and Persistence
The header defines transient state only. `bcm_vk_dma` contents are owned by a pending work entry and should be freed exactly once after firmware response, drain, or error cleanup.

## Dependencies and Integration Points
It depends on Linux DMA mapping types and is included by `bcm_vk_msg.h`, `bcm_vk_msg.c`, and `bcm_vk_sg.c`. The packed `_vk_data` layout is shared with the VK UAPI message protocol and firmware SGL parser.

## Risks and Edge Cases
Because `_vk_data.address` is rewritten in place, callers must not expect the original user pointer after successful allocation. The SGL header is documented as little-endian `u32` words, but the implementation writes native `u32` values. Ownership and cleanup rely on `sglist != NULL`.

## Test Signals
Validate SGL header words, packed `_vk_data` size/alignment, allocation/free API use for every transfer command path, and cleanup idempotence for empty descriptors.
