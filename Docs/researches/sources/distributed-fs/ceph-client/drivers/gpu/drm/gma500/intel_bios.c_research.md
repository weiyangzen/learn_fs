<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.c

## Purpose

This file parses Intel VBT/BDB data for GMA500. It obtains VBT data from the ACPI OpRegion or PCI ROM, walks BIOS data blocks, and extracts panel modes, LVDS/backlight settings, child device mappings, SDVO mappings, driver feature flags, DPLL reference hints, and eDP link/power parameters.

## Important APIs, Types, And Functions

Exported functions are `psb_intel_init_bios()` and `psb_intel_destroy_bios()`. Important internal functions include `find_section()`, `parse_edp()`, `get_blocksize()`, `fill_detail_timing_data()`, `parse_backlight_data()`, `parse_lfp_panel_data()`, `parse_sdvo_panel_data()`, `parse_general_features()`, `parse_sdvo_device_mapping()`, `parse_driver_features()`, and `parse_device_mapping()`.

## Control Flow

Initialization sets `panel_type` invalid, validates and uses OpRegion VBT if present, otherwise maps PCI ROM and scans for `$VBT`. It derives the BDB pointer from the VBT offset and then parses general features, driver features, LFP panel data, SDVO panel data, SDVO mappings, generic child-device mappings, LVDS backlight data, and eDP data. Section lookup starts after the BDB header and walks ID/size-prefixed blocks. Panel timing conversion expands packed DVO timing fields into a DRM mode, fixes bogus totals shorter than sync end, and marks the mode preferred. Destroy frees allocated VBT-derived mode/backlight data.

## State And Persistence

Parsed state persists in `drm_psb_private`: `panel_type`, `lvds_dither`, `lvds_vbt`, `lfp_lvds_vbt_mode`, `sdvo_lvds_vbt_mode`, `lvds_bl`, `int_tv_support`, `int_crt_support`, `lvds_use_ssc`, `lvds_ssc_freq`, `sdvo_mappings`, `child_dev`, `child_dev_num`, `edp` fields, `lvds_enabled_in_vbt`, and `dplla_96mhz`. PCI ROM mapping is temporary and unmapped before return.

## Dependencies And Integration Points

It depends on DRM mode helpers, DP constants, PCI ROM access, opregion state from the core driver, packed layout declarations in `intel_bios.h`, and downstream LVDS/DP/HDMI output discovery.

## Risks And Test Signals

Risks include limited bounds validation while walking BDB sections, assuming child device struct size exactly matches, `parse_backlight_data()` using `bl_start + 1` without a null check after finding options, memory ownership for `child_dev` not freed in the shown destroy path, and trusting firmware timing/link data. Test signals are OpRegion VBT and ROM VBT systems, missing `$VBT`, malformed/short BDB sections, LVDS/eDP mode discovery, DPLL 96 MHz flag behavior, child-device DP/eDP detection, backlight data parsing, and cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/intel_bios.c -->
