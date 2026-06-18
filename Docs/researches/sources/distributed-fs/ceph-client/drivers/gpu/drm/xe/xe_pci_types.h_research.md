<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_types.h

## Purpose

`xe_pci_types.h` defines the descriptor structures that translate PCI IDs and graphics/media IP versions into Xe runtime capability flags.

## Important APIs and Types

`struct xe_subplatform_desc` maps subplatform enum values to names and PCI ID lists. `struct xe_device_desc` is the platform-level descriptor used from the PCI ID table: it contains pre-GMD graphics/media IP pointers, platform/subplatform names, DMA/VA/VM sizing, tile/GT limits, VRAM flags, force-probe and dGFX flags, and feature bits such as display, SR-IOV, flat CCS, PXP, GSC, HECI, I2C, pcode/mtcfg skips, page reclaim assist, and shared VF workqueue needs. `struct xe_graphics_desc`, `struct xe_media_desc`, and `struct xe_ip` describe IP-version-specific engines and features.

## Control Flow and State

The structures are immutable descriptor inputs to PCI probe. `xe_pci.c` copies selected fields into `xe->info`, uses subplatform lists to refine platform identity, and uses IP descriptors to allocate GTs and set engine masks.

## Dependencies and Integration Points

It includes `xe_platform_types.h` for platform enums and Linux types. The definitions are central to PCI probing, GT allocation, display gating, VM/page-table sizing, SR-IOV feature exposure, PM policy, and workarounds.

## Risks and Test Signals

Bitfield packing keeps descriptors compact but makes initialization omissions easy. Feature bits must reflect hardware and firmware expectations exactly. Test signals include descriptor snapshot tests, KUnit coverage for IP lookup, compile checks when adding new feature bits, and boot probes on each platform family validating `xe->info` fields and engine masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pci_types.h -->
