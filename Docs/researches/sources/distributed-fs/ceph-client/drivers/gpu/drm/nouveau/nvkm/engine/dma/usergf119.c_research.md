<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf119.c

## Purpose

`usergf119.c` implements GF119-style DMA object encoding.

## Important APIs, Types, And Functions

`struct gf119_dmaobj` stores generic state plus `flags0`. `gf119_dmaobj_bind()` creates a 24-byte descriptor with flags and 256-byte shifted start/limit. `gf119_dmaobj_new()` parses optional `gf119_dma_v0` kind/page fields, supplies pitch/small-page defaults for real targets and VM/large-page defaults for VM targets, validates page, and encodes VRAM target bits.

## Control Flow

Generic parsing normalizes target/access/range. GF119-specific parsing sets kind and page, then target encoding either marks VRAM or leaves VM/PCI/PCI_NOSNOOP as placeholder-style descriptors used mainly for push buffers. Binding materializes the descriptor into channel memory.

## State And Persistence Behavior

The object persists `flags0` and the generic address range. Start and limit are stored in the descriptor shifted by 8 bits.

## Dependencies And Integration Points

It depends on NVIF GF119 DMA arguments, GPU object helpers, and FIFO/channel users that understand GF119 descriptor semantics.

## Risks And Edge Cases

The file explicitly notes that real PCI/VM descriptors are not fully understood and are used as placeholders for push buffers. Access flags are not encoded here the way older generations do, so callers must not expect full access control from this descriptor.

## Test Signals

Signals include successful pushbuffer DMA object creation for VM/PCI targets, VRAM descriptor operation, page validation errors for invalid input, and no channel setup failures on GF119-era GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf119.c -->
