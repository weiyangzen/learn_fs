# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_vram_freq.c

## Purpose

`xe_vram_freq.c` creates read-only sysfs files that report fused HBM/VRAM frequency points for supported tiles. It currently exposes PVC-only `device/tile#/memory/freq0/max_freq` and `min_freq`.

## Important APIs, Types, and Functions

The exported initializer is `xe_vram_freq_sysfs_init(struct xe_tile *tile)`. Sysfs show handlers are `max_freq_show()` and `min_freq_show()`, both using `xe_pcode_read()` with `PCODE_FREQUENCY_CONFIG`, HBM domain selection, and fused P0 or PN subcommands. `dev_to_tile()` maps a sysfs device back to the tile via `kobj_to_tile()`. `vram_freq_sysfs_fini()` removes the attribute group and drops the kobject through devm cleanup.

## Control Flow and State

Initialization is a no-op unless `xe->info.platform == XE_PVC`. On PVC it creates a `memory` kobject below the tile sysfs kobject, registers the `freq0` attribute group, and stores managed cleanup through `devm_add_action_or_reset()`. Reads issue a pcode mailbox command and multiply the returned fused frequency unit by 50 MHz before formatting the value.

## Dependencies and Integration Points

This file depends on Linux sysfs, DRM managed cleanup, Xe tile sysfs, pcode mailbox APIs, pcode command definitions, and platform detection. It integrates with tile sysfs initialization and exposes firmware-reported fuse data to userspace.

## Risks and Edge Cases

Sysfs reads can fail with pcode errors and propagate negative errno to userspace. The kobject parent relationship assumes the attribute device sits below the tile kobject. The values are fused fixed points, not live configuration knobs; they are deliberately read-only. Platform gating prevents creating misleading files on non-PVC hardware.

## Test Signals

Tests should verify no sysfs group appears on non-PVC platforms, PVC creates `memory/freq0/max_freq` and `min_freq`, pcode failures propagate, returned values are scaled by 50, cleanup removes the group, and repeated probe/remove cycles do not leak kobjects.
