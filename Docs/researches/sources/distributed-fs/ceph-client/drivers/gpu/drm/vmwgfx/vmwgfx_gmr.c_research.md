# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_gmr.c

## Purpose
`vmwgfx_gmr.c` emits SVGA FIFO commands to bind and unbind Guest Memory Regions using the GMR2 command set. It translates vmwgfx scatter-gather page iterators into PPN remap payloads understood by the virtual SVGA device.

## Important APIs, Types, and Functions
- `VMW_PPN_SIZE` selects 32-bit or 64-bit page-number payload width from `sizeof(unsigned long)`.
- `VMW_PPN_PER_REMAP` caps each remap command to a future-safe payload size.
- `vmw_gmr2_bind()` reserves FIFO space, emits `SVGA_CMD_DEFINE_GMR2`, then one or more `SVGA_CMD_REMAP_GMR2` commands containing DMA page numbers.
- `vmw_gmr2_unbind()` emits a zero-page `DEFINE_GMR2` to release a GMR id.
- `vmw_gmr_bind()` and `vmw_gmr_unbind()` are the exported capability-gated wrappers.

## Control Flow
Binding starts a `vmw_piter` over a vmwgfx sg table, returns success for empty mappings, rejects devices without `SVGA_CAP_GMR2`, and reserves a single FIFO region sized for the define command plus all remap chunks. Each remap chunk fills offset, count, 32/64-bit flags, and sequential PPNs from the DMA iterator before committing the FIFO reservation. Unbind reserves and commits a small define command with `numPages = 0`.

## State and Persistence Behavior
The file does not allocate ids or maintain state; it programs host-visible SVGA GMR mappings for ids allocated elsewhere. Binding persists in the virtual device until unbound or reset. The source sg table and iterator state are consumed only during command construction.

## Dependencies and Integration Points
It depends on vmwgfx FIFO reservation/commit helpers, `struct vmw_sg_table`, `struct vmw_piter`, DMA addresses, and SVGA register command definitions. TTM placement and execbuf relocation ultimately depend on these mappings when BOs reside in GMR space.

## Risks
The command size calculation must match the exact emitted payload, and the `BUG_ON` asserts that the buffer cursor ends where expected. Large mappings are split to avoid oversized remaps, but the total FIFO reservation can still fail. Page-number width must match host/device expectations. Devices without GMR2 support intentionally reject binds.

## Test Signals
Test empty sg tables, single-page and multi-chunk mappings, 32-bit and 64-bit PPN builds, FIFO reserve failure, GMR2 capability absence, and unbind during BO eviction. Device-side display or DMA failures after relocation are likely signals of malformed GMR binding.
