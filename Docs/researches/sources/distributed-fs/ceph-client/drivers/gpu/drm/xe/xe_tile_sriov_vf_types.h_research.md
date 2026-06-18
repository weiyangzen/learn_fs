<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf_types.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf_types.h

## Purpose

`xe_tile_sriov_vf_types.h` defines the VF per-tile self-configuration data.

## Important APIs, Types, and Functions

`struct xe_tile_sriov_vf_selfconfig` stores assigned GGTT base, GGTT size, and LMEM size.

## Control Flow

VF provisioning stores values after querying PF/GuC-assigned resources. Other VF code reads them for memory management and post-migration address fixups.

## State and Persistence Behavior

The struct is embedded in the VF arm of `struct xe_tile.sriov` and persists for the tile lifetime.

## Dependencies and Integration Points

It depends on Linux types and is included by tile types and VF tile helpers.

## Risks and Test Signals

Incorrect base/size values can corrupt GGTT rebasing or resource bounds. Tests should check initialization to zero and updates after provisioning query.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf_types.h -->
