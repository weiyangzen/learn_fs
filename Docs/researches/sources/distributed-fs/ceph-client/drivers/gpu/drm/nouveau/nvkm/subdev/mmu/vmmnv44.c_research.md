# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mmu/vmmnv44.c

## Purpose
Implements NV44 packed-page-table VMM support. Four 27-bit page-frame entries are packed across four 32-bit words, with dummy-page fill for unmapped entries.

## Important APIs, Types, And Functions
Exports `nv44_vmm_new`. Internal helpers include `nv44_vmm_pgt_fill`, `nv44_vmm_pgt_{pte,sgl,dma,unmap}`, and `nv44_vmm_flush`.

## Control Flow
`nv44_vmm_pgt_fill` read-modify-writes a four-entry group so partial updates preserve neighboring PTEs. Full groups are written directly. Unmap fills entries with `vmm->null`, allocated as a 16 KiB coherent dummy page during construction if possible. Flush writes limit and command registers at `0x100814`/`0x100808`, polls, then clears the command.

## State And Persistence
Persistent state includes packed PGT words, a coherent dummy-page allocation (`vmm->nullp`/`vmm->null`), and hardware TLB state. Dummy allocation failure degrades to null address zero with a warning.

## Dependencies And Integration Points
Depends on NV04 validation, timer polling, DMA coherent allocation, and generic VMM destructor ownership of `vmm->nullp` if present. It is selected for NV44-style host-only page tables.

## Risks And Test Signals
Risks include partial group corruption, off-by-one loop behavior in unmap, dummy-page allocation failure, and packed bitfield errors. Test unaligned PTE ranges, ranges crossing four-entry groups, unmap holes, PAGE_SHIFT variants, and flush timeout behavior.
