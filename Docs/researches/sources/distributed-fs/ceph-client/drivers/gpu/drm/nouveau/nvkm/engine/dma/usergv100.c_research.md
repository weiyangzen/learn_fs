<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergv100.c

## Purpose

`usergv100.c` implements GV100/Volta DMA object encoding and binding.

## Important APIs, Types, And Functions

`struct gv100_dmaobj` stores generic state plus `flags0`. `gv100_dmaobj_bind()` emits a 24-byte descriptor with flags and separate low/high dwords for start and limit, both shifted by 8. `gv100_dmaobj_new()` reuses the GF119 argument shape for kind/page, coerces them to booleans, defaults to small-page pitch-like settings when no tail is provided, sets read/write, and encodes VRAM/PCI/PCI_NOSNOOP targets.

## Control Flow

The shared constructor parses generic arguments. GV100-specific parsing sets optional kind/page bits. Binding creates the GPU object descriptor used by later channel setup.

## State And Persistence Behavior

Persistent state is the normalized address range/target plus `flags0`. Unlike GF119, GV100 requires concrete VRAM or PCI targets and rejects VM.

## Dependencies And Integration Points

It depends on GPU object allocation, NVIF DMA argument structures, and Volta+ FIFO/channel paths.

## Risks And Edge Cases

VM targets are rejected here; clients expecting GF119 placeholder behavior will fail. Kind/page inputs are booleanized rather than preserving full numeric values. Address encoding assumes 256-byte granularity.

## Test Signals

Test VRAM/PCI/PCI_NOSNOOP object creation, rejection of VM targets, descriptor binding, and successful channel pushbuffer operation on GV100-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergv100.c -->
