<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.h

## Purpose

`ior.h` defines nouveau's display output-resource abstraction. An IOR is the hardware resource that actually drives a connector path: DAC for analog/TV, SOR for LVDS/TMDS/HDMI/DP/eDP, and PIOR for external output resources.

## Important APIs, Types, And Functions

The central type is `struct nvkm_ior`, which stores the display pointer, resource type/id, HDA capability, identity routing flag, armed and assembly states, and protocol-specific DP/TMDS state. `struct nvkm_ior_state` tracks the output path attached to a resource, raster generator divider, EVO protocol, decoded protocol, link selection, and head mask. `struct nvkm_ior_func` is the generation-specific method table for route get/set, state readback, power, load sense, clocking, workarounds, backlight, HDMI, DP, and HDA programming. Helper prototypes expose resource creation/destruction/find and many generation-specific SOR/DAC/PIOR operations from NV50 through TU102/GV100-era hardware.

## Control Flow

The header is a contract rather than an executable unit. Display constructors choose an `nvkm_ior_func` table per chipset, create IORs with `nvkm_ior_new_()`, and later output-path code attaches `struct nvkm_outp` objects to the IOR `asy` state. Supervisor code reads `arm` and `asy` with `func->state`, performs BIOS scripts and link programming, then arms hardware. DP/HDMI/HDA userspace methods reach the generation hooks through the nested function tables.

## State And Persistence Behavior

IOR objects are persistent display-engine objects stored on `disp->iors`. `arm` mirrors hardware state and `asy` is the next assembled modeset state. DP lane count, bandwidth, enhanced framing, MST, and TMDS high-speed flags are kept in the IOR because they affect later supervisor and audio/link callbacks.

## Dependencies And Integration Points

This file ties together `priv.h`, output paths, DP AUX, connector/user wrappers, BIOS display tables, and generation files such as `nv50.c`, `gf119.c`, `gm200.c`, `gv100.c`, and `tu102.c`.

## Risks And Edge Cases

The function table is sparse by generation; callers must check optional hooks before use. `nv50_sor_link()` depends on `asy.link`, so stale assembly state can address the wrong register lane. Route callbacks are only present on later dynamic-routing SORs. Identity-mapped panel outputs must not be reassigned casually because backlight and panel wiring can be tied to a specific SOR.

## Test Signals

Useful signals are correct IOR enumeration in boot logs, successful mode inheritance from firmware, DP/HDMI link training without missing hook failures, HDA audio hotplug/ELD events on HDA-capable SORs, and backlight operations working only on IORs with `bl` hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.h -->
