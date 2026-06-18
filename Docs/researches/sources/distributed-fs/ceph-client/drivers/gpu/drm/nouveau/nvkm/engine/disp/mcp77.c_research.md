<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp77.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp77.c

## Purpose

`mcp77.c` supplies the display function table for MCP77-family integrated GPUs. It reuses the NV50 EVO display core while selecting G94-style SOR behavior and GT206 class IDs.

## Important APIs, Types, And Functions

`mcp77_sor` is the SOR method table. It combines `g94_sor_state`, `nv50_sor_power`, `nv50_sor_clock`, NV50 backlight, G84 HDMI, and G94 DP support. `mcp77_sor_new()` wraps that table with `nvkm_ior_new_()`. `mcp77_disp` is the full `nvkm_disp_func` descriptor: NV50 oneinit/init/fini/intr/super, NV50 heads/DAC/PIOR, G94 SOR count, GT206 root class, and G82/GT200/GT206 user channel classes. `mcp77_disp_new()` constructs the engine through `nvkm_disp_new_()`.

## Control Flow

Probe reaches `mcp77_disp_new()`, which installs `mcp77_disp`. During oneinit, shared NV50 code enumerates heads, DACs, SORs, PIORs, outputs, and connectors. SOR creation calls `mcp77_sor_new()`, giving each SOR the MCP77-specific capability mix. Runtime mode changes use the inherited NV50 supervisor and channel paths.

## State And Persistence Behavior

No private state is introduced. Persistent state lives in the generic `nvkm_disp`, `nvkm_ior`, output, connector, and channel objects created by shared constructors.

## Dependencies And Integration Points

The file depends on `priv.h`, `chan.h`, `head.h`, `ior.h`, NVIF display class IDs, NV50 display core helpers, G94 SOR helpers, G84 HDMI, and GT200/G94 user channel descriptors from neighboring display files.

## Risks And Edge Cases

The table must match MCP77 hardware class IDs and SOR capabilities. A wrong SOR count or class mapping would expose unusable channels or miss DP/HDMI features. HDA is not enabled in `nvkm_ior_new_()`, unlike MCP89.

## Test Signals

Boot should report MCP77 display resources, modesets should exercise NV50 supervisor phases, HDMI and DP paths should work through G84/G94 hooks, and user channels should instantiate with the GT206/G82/GT200 class mix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp77.c -->
