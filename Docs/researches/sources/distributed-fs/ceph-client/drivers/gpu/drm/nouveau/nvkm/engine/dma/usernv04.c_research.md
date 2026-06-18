<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv04.c

## Purpose

`usernv04.c` implements legacy NV04 DMA object encoding, including special VM clone behavior for old MMUs.

## Important APIs, Types, And Functions

`struct nv04_dmaobj` stores generic state, `clone`, `flags0`, and `flags2`. `nv04_dmaobj_bind()` emits a 16-byte descriptor with class/target/access flags, length, and offset; in clone mode it can wrap the legacy page table or read a page-table entry to derive the physical offset. `nv04_dmaobj_new()` normalizes generic arguments, converts VM targets to PCI/RW on NV04 MMU, selects target flags, and encodes access flags.

## Control Flow

Creation calls the shared constructor, handles VM target special cases, computes flags from target/access, and returns the object. Binding later allocates or wraps a GPU object descriptor and writes the legacy DMA object fields.

## State And Persistence Behavior

The object persists clone mode and descriptor flags. In clone mode, binding may depend on the current legacy MMU page table contents.

## Dependencies And Integration Points

It depends on GPU object helpers, framebuffer target constants, legacy MMU/VMM structures, and channel code that consumes 16-byte DMA descriptors.

## Risks And Edge Cases

The length is computed as `limit - start`, matching legacy descriptor expectations; off-by-one assumptions must not be changed without hardware validation. Clone mode reads page table entries and assumes the old MMU layout. Write-only access falls through to set writable bits.

## Test Signals

Signals include successful VRAM/PCI/PCI_NOSNOOP descriptors, VM clone descriptors on NV04 MMU, correct access enforcement, and working legacy FIFO push buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv04.c -->
