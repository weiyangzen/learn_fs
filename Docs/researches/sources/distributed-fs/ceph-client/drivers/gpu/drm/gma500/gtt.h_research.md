<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.h

## Purpose

This header defines the GMA500 GTT state structure and public GTT management API.

## Important APIs, Types, And Functions

`struct psb_gtt` stores `gatt_start`, `mmu_gatt_start`, `gtt_start`, `gtt_phys_start`, GTT/GATT page counts, and stolen-memory size fields. It declares init/fini/resume, resource allocation, PTE encoding, page insertion, and page removal functions.

## Control Flow

No executable flow exists. GEM and driver init/resume paths call into the declared functions to reserve GPU address space and program hardware PTEs.

## State And Persistence

The struct is embedded in `drm_psb_private` and persists for the device lifetime. Its values define address-space boundaries used by every GEM object.

## Dependencies And Integration Points

It includes DRM GEM for related types and forward-declares `drm_psb_private`. It is consumed by GEM, driver init/fini, and display pinning paths.

## Risks And Test Signals

Risks include 32-bit address fields limiting larger apertures, duplicated stolen-size fields between `psb_gtt` and `drm_psb_private`, and API coupling to Linux `struct resource`. Test signals are compile coverage, allocation boundary tests, stolen/system range separation, and resume consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/gtt.h -->
