<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.c

## Purpose

`xe_pci.c` is the PCI driver front door for Xe. It binds Intel PCI IDs to static device descriptors, enforces force-probe policy, initializes early device/platform/IP information, allocates tiles and GTs, wires the DRM device into PCI probe/remove/shutdown, and provides system/runtime PM callbacks for PCI D-states.

## Important APIs, Types, and Functions

The file defines static `xe_graphics_desc`, `xe_media_desc`, `xe_ip`, and `xe_device_desc` tables for platforms from Tigerlake through Novalake/Crescent Island. `pciidlist[]` maps PCI IDs to descriptors and registers with `MODULE_DEVICE_TABLE`. Helper functions include `device_id_in_list()`, `id_forced()`, `id_blocked()`, `find_subplatform()`, `read_gmdid()`, `find_graphics_ip()`, `find_media_ip()`, `handle_gmdid()`, `xe_info_init_early()`, `xe_info_probe_tile_count()`, `alloc_primary_gt()`, `alloc_media_gt()`, and `xe_info_init()`. Driver entry points are `xe_pci_probe()`, `xe_pci_remove()`, `xe_pci_shutdown()`, PM callbacks, `xe_pci_to_pf_device()`, `xe_register_pci_driver()`, and `xe_unregister_pci_driver()`.

## Control Flow and State

Probe checks configfs, force-probe allow/deny lists, display deferral, enables the PCI device, creates `xe_device`, stores DRM drvdata, disables PM for unbound bridges, initializes descriptor-only info and the root tile, optionally resizes ReBAR, performs early device probe, handles boot survivability, reads GMD_ID or pre-GMD descriptors, allocates remote tiles/VRAM/GTs, probes display, initializes PM, probes the full device, then enables runtime PM. Remove disables SR-IOV VFs for PFs, skips normal teardown in survivability mode, then removes device state and PM. System sleep calls `xe_pm_suspend()`/`xe_pm_resume()` around PCI state save/restore and D3cold transitions. Runtime suspend/resume toggles D3cold based on `xe->d3cold.allowed`.

## Dependencies and Integration Points

This file integrates Linux PCI/PM/runtime-PM, DRM driver registration, Intel PCI ID macros, configfs feature gating, SR-IOV VF/PF helpers, GMD_ID MMIO, GuC VF bootstrap for GMD_ID reads, display probe, tile/GT allocation, ReBAR, pcode, PM, and survivability mode. KUnit static stubs are present for selected discovery helpers.

## Risks and Test Signals

Descriptor table correctness drives almost every downstream feature bit; wrong fields can mis-size VA, DMA masks, GT counts, engine masks, SR-IOV support, display, flat CCS, PXP, or PM behavior. GMD_ID reads for VFs allocate a temporary GT and can fail early. Force-probe parsing accepts wildcards and negative lists, so module parameter tests are important. Runtime PM asserts no VF lifetime during PF runtime suspend. Test signals include PCI ID matching, force-probe allow/block behavior, descriptor feature snapshots, GMD_ID unknown version rejection, media-fused-off handling, configfs GT gating, tile count reduction from MTCFG, probe error injection cleanup, SR-IOV PF lookup from VF, and D3hot/D3cold suspend/resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci.c -->
