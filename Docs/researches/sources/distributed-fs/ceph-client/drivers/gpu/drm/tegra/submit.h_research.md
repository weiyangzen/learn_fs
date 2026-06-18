# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/submit.h

## Purpose

`submit.h` declares shared data structures for Tegra DRM job submission and the firmware firewall validator used by `submit.c` and engine-specific validation code.

## Important APIs, Types, and Functions

- `struct tegra_drm_used_mapping` records a `tegra_drm_mapping` reference plus submit buffer flags for each mapping used by a job.
- `struct tegra_drm_submit_data` stores the dynamically allocated array of used mappings and its count; it is attached to `host1x_job.user_data`.
- `tegra_drm_fw_validate()` validates gather words for a given client, updates current job class, and receives relocation/mapping metadata.

## Control Flow

The header itself has no control flow. `submit.c` fills `tegra_drm_submit_data` after copying user buffer descriptors, passes it into `tegra_drm_fw_validate()` per gather command, then releases all contained mappings from the host1x job release callback.

## State and Persistence Behavior

The structures are per-submit transient state. Their mapping references persist until the host1x job is released, preventing buffers from being unmapped while hardware can still access them.

## Dependencies and Integration Points

It depends on definitions of `struct tegra_drm_mapping`, `struct tegra_drm_client`, and fixed-width `u32` from surrounding Tegra DRM headers. It is included by `submit.c` and by firewall validation implementations.

## Risks and Edge Cases

Because ownership is by convention, callers must ensure every mapping stored in `used_mappings` has an active ref and that cleanup runs exactly once. The validator contract is not documented here beyond its signature, so class mutation and mapping flag semantics must be inferred from implementations.

## Test Signals

Compile coverage verifies structure visibility. Runtime submission tests should assert mapping refs remain held while jobs are live and are dropped on every success and failure path.
