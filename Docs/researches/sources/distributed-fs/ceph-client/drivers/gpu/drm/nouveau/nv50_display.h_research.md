# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nv50_display.h

## Purpose
This header declares the NV50 display creation entry point and includes display/register dependencies needed by NV50-era display and fence code.

## Important APIs, Types, and Functions
It declares `nv50_display_create(struct drm_device *)`.

## Control Flow
There is no executable flow. The declaration allows higher-level driver code to instantiate NV50 display support.

## State and Persistence Behavior
The header stores no state. The implementation creates display state elsewhere.

## Dependencies and Integration Points
It includes `nouveau_display.h` and `nouveau_reg.h`. Fence files include it for chipset-era shared declarations even though they primarily handle fences.

## Risks
The risk is limited to signature drift and unnecessary include coupling between display and fence code.

## Test Signals
Build coverage and NV50 display initialization tests catch interface breakage.
