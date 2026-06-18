<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf100.c

## Purpose

`usergf100.c` implements GF100/Fermi DMA object encoding and binding.

## Important APIs, Types, And Functions

`struct gf100_dmaobj` extends the generic DMA object with `flags0` and `flags5`. `gf100_dmaobj_bind()` creates a 24-byte GPU object and writes flags, limit/start low bits, packed high address bits, zero padding, and flags5. `gf100_dmaobj_new()` parses optional `gf100_dma_v0` tail arguments for kind and privilege, supplies defaults for VM or pitch objects, validates privilege, and encodes target/access bits.

## Control Flow

Creation calls the shared constructor first, then consumes optional GF100 arguments if present. With no tail args, non-VM targets default to pitch/user mode and VM targets default to VM/priv mode. Binding later emits the hardware descriptor into a parent GPU object.

## State And Persistence Behavior

Persistent per-object state is the normalized generic range/target/access plus `flags0` and `flags5`. The bound GPU object is separate and owned by the caller.

## Dependencies And Integration Points

It depends on NVIF GF100 DMA argument definitions, GPU object allocation, framebuffer target constants, and FIFO channel bind paths.

## Risks And Edge Cases

The access switch does not explicitly reject unknown access values after the known cases, so correctness relies on the shared constructor's normalization. Kind is not range-checked in this file beyond what userspace provides. The unknown `unkn` field defaults differently for VM and pitch paths.

## Test Signals

Test default VM/pitch object creation, explicit kind/priv arguments, target/access combinations, and correct channel operation after binding the 24-byte descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf100.c -->
