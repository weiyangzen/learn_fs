<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.h

## Purpose

`xe_tile_sriov_vf.h` declares VF tile self-configuration accessors.

## Important APIs, Types, and Functions

It exposes getters and setters for VF GGTT size, GGTT base, and LMEM size.

## Control Flow

VF provisioning and migration recovery update values; GGTT/LMEM consumers read them through this interface.

## State and Persistence Behavior

The APIs operate on `tile->sriov.vf.self_config` persistent state.

## Dependencies and Integration Points

It depends on Linux types and forward-declares `xe_tile`. It is consumed by VF provisioning, GGTT setup, and migration fixup paths.

## Risks and Test Signals

Callers must pass VF-mode tiles. Tests should verify values survive across the relevant provisioning and recovery phases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_tile_sriov_vf.h -->
