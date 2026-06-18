<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.c

## Purpose

`outp.c` implements generic display output-path objects. It maps DCB output records to compatible IOR protocols, inherits firmware routes, acquires/releases output resources for userspace and private operations, performs basic HPD detection, and dispatches backlight operations.

## Important APIs, Types, And Functions

`nvkm_outp_xlat()` maps DCB location/type pairs to IOR type and protocol. `nvkm_outp_acquire_or()`, `nvkm_outp_acquire_ior()`, and `nvkm_outp_acquire_hda()` select an output resource, preferring already armed resources, non-HDA SORs when audio is unnecessary, HDA SORs when requested, and identity-mapped panel SORs when required. `nvkm_outp_route()` applies route changes to dynamic-routing hardware. `nvkm_outp_release_or()` and `nvkm_outp_release()` clear acquisition bits and route state. `nvkm_outp_inherit()` discovers firmware-selected routes. `nvkm_outp_init()` records inherited active outputs and disables stale routed DP links when needed. `nvkm_outp_detect()` handles basic HPD. `nvkm_outp_new_()` and `nvkm_outp_new()` construct output objects.

## Control Flow

Display oneinit creates output paths from DCB entries using `nvkm_outp_new()` or DP-specific constructors. Init calls inherit/readback code so existing firmware modes can be represented. Userspace acquire methods call `func->acquire`, which eventually updates `outp->ior`, `ior->asy.outp`, and acquisition bits, then `nvkm_outp_route()` transitions route hardware. Release clears user state and applies route updates. Private helpers temporarily acquire output resources for load detect or backlight work.

## State And Persistence Behavior

`struct nvkm_outp` persists DCB metadata, I2C bus pointer, connector pointer, identity flag, acquisition bitmask, current IOR pointer, protocol-specific LVDS/DP state, and its user object. `ior->arm.outp` is the current hardware attachment and `ior->asy.outp` is the assembled next attachment.

## Dependencies And Integration Points

The file depends on BIOS DCB data, GPIO HPD, I2C, DP helpers, connector objects, IOR generation hooks, and NVKM object lifetime. It is used by display oneinit, user output wrappers, DP link training, HDMI/HDA methods, load detection, and backlight control.

## Risks And Edge Cases

The acquisition algorithm has many policy branches. Wrong identity handling can break LVDS/eDP panels, and wrong HDA preference can lose audio. `nvkm_outp_detect()` intentionally returns unknown for many non-DP no-HPD cases, leaving DDC probing to DRM. `nvkm_outp_init()` only records inherited modes when protocol and head state match.

## Test Signals

Useful checks are successful mode inheritance after firmware boot, stable OR assignment across modesets, panel backlight working on identity SORs, DP stale-route disable logs only when expected, and HPD/detect results matching physical connector changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.c -->
