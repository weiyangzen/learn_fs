<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.c

## Purpose

This file manages GMA500 GTT address-space allocation and hardware page-table programming. It enables/disables the chipset GTT, maps the GTT table, clears it to a scratch page, allocates ranges for stolen/system-backed GEM objects, inserts/removes PTEs, and reinitializes ranges after resume.

## Important APIs, Types, And Functions

Exported functions are `psb_gtt_allocate_resource()`, `psb_gtt_mask_pte()`, `psb_gtt_insert_pages()`, `psb_gtt_remove_pages()`, `psb_gtt_init()`, `psb_gtt_fini()`, and `psb_gtt_resume()`. Internal helpers are `psb_gtt_entry()`, `psb_gtt_enable()`, `psb_gtt_disable()`, `psb_gtt_clear()`, and `psb_gtt_init_ranges()`.

## Control Flow

Initialization creates the GTT mutex, enables GMCH/PGETBL, derives GTT/GATT physical and logical ranges from PCI BARs or Cedarview fallback values, ioremaps the GTT table, and fills all entries with the scratch page. Resource allocation reserves from the stolen prefix for stolen objects or the remaining range for system objects. Insertion locks the GTT mutex, writes one PTE per backing page, and reads back the last slot to flush. Removal replaces object PTEs with the scratch page. Resume re-enables the GTT, recomputes ranges, verifies page count did not change, clears entries, then disables the GTT on exit from the helper.

## State And Persistence

State lives in `drm_psb_private.gtt`, `gtt_mem`, `gtt_map`, saved `gmch_ctrl`, saved `pge_ctl`, `gtt_mutex`, and scratch page. Hardware state is the GMCH GTT-enable bit, PGETBL control register, and GTT PTE contents. Resource tree children persist as GEM allocations.

## Dependencies And Integration Points

It depends on PCI resources/config, PSB register access macros, `struct psb_gem_object` for resume resource walking elsewhere, and GEM pinning/removal paths.

## Risks And Test Signals

Risks include fallback fake GATT resources on CDV, 32-bit PFN BUG_ON for high memory, clearing GTT during resume before GEM repopulation, `psb_gtt_resume()` disabling GTT after clearing, and resource fragmentation/exhaustion. Test signals are GTT init/fini, stolen/system allocations, PTE readback, pin/unpin cycles, suspend/resume with pinned objects, CDV missing BAR fallback, and scratch-page mapping after removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.c -->
