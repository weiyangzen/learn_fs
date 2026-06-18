# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/mid_bios.c

## Purpose
This file discovers Moorestown/Oaktrail platform configuration that is not supplied by normal desktop VBT paths. It reads fuse values, SKU/core-clock data, panel type, panel timing, MIPI/LVDS descriptors, and PCI revision data into `drm_psb_private` before display output setup.

## Important APIs, Types, and Functions
The public entry point is `mid_chip_setup()`. `mid_get_fuse_settings()` reads host bridge configuration windows for display type and SKU frequency. `mid_get_pci_revID()` records the graphics root revision. `read_vbt_r0()` and `read_vbt_r10()` map the platform GCT header. `mid_get_vbt_data_r0()`, `_r1()`, and `_r10()` parse different GCT layouts into `dev_priv->gct_data`; `mid_get_vbt_data()` chooses the parser by `$GCT` revision.

## Control Flow
`mid_chip_setup()` runs fuse discovery, GCT/VBT discovery, and revision discovery. Fuse discovery obtains PCI bus 0 device 0, writes magic addresses to config offset `0xD0`, reads through `0xD4`, sets `iLVDS_enable`, `is_lvds_on`, `is_mipi_on`, `video_device_fuse`, `fuse_reg_value`, and `core_freq`. GCT discovery reads config offset `0xFC` from graphics root, maps the header, validates signature, then maps the revision-specific panel table and copies the selected boot panel timing into common `oaktrail_gct_data`.

## State and Persistence Behavior
The file persists platform facts in `drm_psb_private`: selected internal display type, initial LVDS/MIPI power flags, core frequency, fuse values, platform revision, `has_gct`, and `gct_data`. The mapped GCT memory is temporary and unmapped after copies. No firmware data is written except the PCI config address-window setup used for fuse reads.

## Dependencies and Integration Points
It depends on PCI config-space access, `ioremap()` of firmware-provided physical addresses, Oaktrail GCT structures from `oaktrail.h`, and display setup in `oaktrail_device.c` and `oaktrail_lvds.c`. If no GCT is found, Oaktrail setup falls back to OpRegion and normal Intel BIOS parsing.

## Risks
The code trusts several firmware-provided sizes and panel indexes with limited bounds checking, especially GCT revision 0/1 boot panel indexes and revision 1.0 `panel_count`. The comments note missing ioremap-failure checks in older paths. Bad fuse reads can select wrong LVDS/MIPI behavior or core clock, which affects PLL and backlight calculations.

## Test Signals
Boot logs should identify internal LVDS/MIPI selection, SKU/core clock, and GCT revision. Oaktrail LVDS should get a fixed mode from `gct_data` when EDID is absent. Invalid or missing GCT should trigger BIOS fallback without crashing. Core clock values should be 100, 166, or 200 MHz for known SKUs.
