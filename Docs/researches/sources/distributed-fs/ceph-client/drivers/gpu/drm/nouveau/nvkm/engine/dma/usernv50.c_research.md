<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv50.c

## Purpose

`usernv50.c` implements NV50 DMA object encoding and binding.

## Important APIs, Types, And Functions

`struct nv50_dmaobj` stores generic state plus `flags0` and `flags5`. `nv50_dmaobj_bind()` creates a 24-byte descriptor with flags, low start/limit, packed high start/limit, zero padding, and partition flags. `nv50_dmaobj_new()` parses optional `nv50_dma_v0` fields for privilege, partition, compression, and kind; supplies defaults for non-VM and VM targets; validates field ranges; and encodes target/access bits.

## Control Flow

Creation starts with generic parsing, then consumes optional NV50-specific tail data. If no tail exists, defaults depend on whether the target is VM. Binding materializes the descriptor into a parent GPU object, commonly under a channel instance block.

## State And Persistence Behavior

Persistent per-object state is generic target/access/range plus encoded flags. The bound descriptor is transient with the caller's GPU object hierarchy.

## Dependencies And Integration Points

It depends on NVIF `nv50_dma_v0`, GPU object allocation, framebuffer target constants, and NV50 FIFO/channel RAMFC paths.

## Risks And Edge Cases

Field range checks reject priv > 2, part > 2, comp > 3, or kind > 0x7f. Access VM is allowed without extra flags, while RO/WO/RW set specific bits. VM defaults use VM partition/compression/kind values and must match hardware expectations.

## Test Signals

Test default and explicit NV50 DMA object creation, invalid tail field rejection, descriptor bind layout, and successful NV50/G8x channel setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv50.c -->
