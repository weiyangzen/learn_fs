<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_printk.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_printk.h

## Purpose

`xe_tile_sriov_printk.h` composes tile-aware and SR-IOV-aware logging for messages that need both PF/VF and tile context.

## Important APIs, Types, and Functions

It defines tile SR-IOV print, err, notice, info, dbg, and verbose dbg macros. Messages are routed through `xe_sriov_*` logging while using the tile prefix format.

## Control Flow

Tile SR-IOV code calls these macros instead of raw tile or SR-IOV logging to include both contexts.

## State and Persistence Behavior

No state is owned. Logs depend on tile ID, device pointer, and SR-IOV mode.

## Dependencies and Integration Points

It includes `xe_tile_printk.h` and `xe_sriov_printk.h`. It is intended for tile-level PF/VF SR-IOV config and diagnostics.

## Risks and Test Signals

Macro composition can obscure format-string errors. Compile coverage under verbose debug enabled/disabled should validate calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_printk.h -->
