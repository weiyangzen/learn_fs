# sources/distributed-fs/ceph-client/drivers/char/agp/intel-gtt.c

## Purpose

`intel-gtt.c` implements Intel GMCH global GTT management for older integrated graphics. Historically it also exposes GTT mapping through a fake AGP bridge so old userspace Intel graphics stacks can bind pages through AGPGART. Modern DRM/i915 can call the exported GMCH helpers directly.

## Important APIs, Types, And Functions

- `struct intel_gtt_driver` abstracts chipset generation, DMA mask, setup/cleanup, PTE read/write, flag validation, and chipset flush hooks.
- `intel_private` stores the selected driver, bridge/GPU PCI devices, MMIO mappings, GTT base and sizes, scratch page, stolen memory, flush page resource, DMA/IOMMU state, and refcount.
- Setup and cleanup: `i810_setup()`, `i830_setup()`, `i9xx_setup()`, `intel_gtt_init()`, `intel_gtt_cleanup()`, `intel_gtt_setup_scratch_page()`, and `intel_gtt_teardown_scratch_page()`.
- PTE operations: `i810_write_entry()`, `i830_write_entry()`, `i965_write_entry()`, and matching read helpers.
- Exported DRM-facing APIs: `intel_gmch_probe()`, `intel_gmch_remove()`, `intel_gmch_enable_gtt()`, `intel_gmch_gtt_insert_page()`, `intel_gmch_gtt_insert_sg_entries()`, `intel_gmch_gtt_read_entry()`, `intel_gmch_gtt_clear_range()`, `intel_gmch_gtt_get()`, and `intel_gmch_gtt_flush()`.
- Fake AGP callbacks under `CONFIG_AGP_INTEL`: `intel_fake_agp_configure()`, `intel_fake_agp_insert_entries()`, `intel_fake_agp_remove_entries()`, `intel_fake_agp_alloc_by_type()`, and the `intel_fake_agp_driver`.

## Control Flow

`intel_gmch_probe()` selects an integrated graphics device either from an explicit GPU PCI device or by scanning known IDs. It optionally installs `intel_fake_agp_driver` into an AGP bridge for gen1 integrated chipsets, refcounts shared ownership, pins bridge/GPU devices, sets DMA masks for AGP callers, and calls `intel_gtt_init()`. Initialization maps chipset registers, determines mappable and total GTT entries, saves PGETBL state, maps the GTT WC if safe, detects stolen memory, allocates a scratch page, and records the graphics aperture bus address.

GTT insertion writes per-page DMA addresses into chipset-specific PTE format, posts the write, and runs a chipset flush hook when present. Fake AGP insertion lazily clears non-stolen mappable GTT on first access, validates flags and bounds, optionally DMA maps scatterlists when VT-d requires the DMA API, and stores SG state for unmap on removal. Removal clears entries back to the scratch page and unmaps SG mappings if needed.

## State And Persistence Behavior

`intel_private` is module-global and refcounted across fake AGP and DRM callers. Persistent hardware state includes PGETBL enable/base, GGTT PTE contents, chipset flush page resources, stolen-memory layout, and scratch-page mappings. GTT entries persist until explicitly cleared, GPU reset, or driver cleanup. `clear_fake_agp` ensures old AGP users do not inherit stale firmware or stolen-memory mappings beyond the stolen region.

## Dependencies And Integration Points

The file depends on `intel-agp.h`, `agp.h`, PCI resource APIs, DMA mapping, optional Intel IOMMU detection, MMIO mapping, and DRM's `drm/intel/intel-gtt.h` exported interface. It is called by `intel-agp.c` during Intel host-bridge probe and by DRM/i915 for direct GTT access. It integrates with chipset-specific cache flush mechanisms, CPU cache attribute APIs, and resource allocation for Intel flush pages.

## Risks And Edge Cases

The code contains a likely stale debug statement in `intel_gtt_unmap_memory()` referencing `mem` in a `DBG()` macro without a local `mem`; this is hidden unless AGP debug expands the macro. Refcounted cleanup is split: `intel_gmch_remove()` tears down scratch/device refs but does not call the full `intel_gtt_cleanup()` path unless fake AGP cleanup runs, so ownership order matters. VT-d on Ironlake disables WC mappings and can require DMA API mappings before inserting pages. GTT total and mappable size detection varies by generation and BIOS GMCH bits; wrong decoding can expose out-of-range entries. PTE packing differs between i830 and i965-style hardware, including high-address bit shifting.

## Test Signals

Build with and without `CONFIG_AGP_INTEL` and `CONFIG_INTEL_IOMMU`. Probe tests should confirm chipset selection, GTT total/mappable logs, stolen-memory detection, scratch-page setup, and DMA mask configuration. Functional tests should insert, read back, clear, and flush GTT entries for single pages and SG tables. Suspend/resume should verify `intel_gmch_enable_gtt()` restores PGETBL. Static tests should compile AGP debug enabled, audit refcount cleanup, and check GTT bounds for fake AGP insertion/removal.
