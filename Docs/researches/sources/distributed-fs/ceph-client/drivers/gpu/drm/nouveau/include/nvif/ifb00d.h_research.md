# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/ifb00d.h

## Purpose
Defines GM200 VMM ABI extensions.

## Important APIs, Types, And Functions
Includes generic VMM definitions, `gm200_vmm_v0` with big-page mode, and `gm200_vmm_map_v0` with volatile, read-only, privilege, and kind fields.

## Control Flow
No executable flow. GM200 VMM object construction and mapping use these payloads.

## State And Persistence
Payloads are transient; GPU virtual mappings persist until unmapped.

## Dependencies And Integration Points
Integrated with `NVIF_CLASS_VMM_GM200`, `nvif/vmm.h`, and GM200 MMU backends.

## Risks
Big-page selection and map attributes must match GM200 hardware descriptor expectations.

## Test Signals
GM200 map/unmap, page-fault logs, and memory-kind tests validate behavior.
