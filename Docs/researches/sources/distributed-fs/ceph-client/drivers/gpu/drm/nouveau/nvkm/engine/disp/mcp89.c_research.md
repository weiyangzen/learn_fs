<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp89.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp89.c

## Purpose

`mcp89.c` defines the MCP89/GT214 display variant. It reuses NV50 display infrastructure but uses GT215-era SOR features, HDA support, and a lane-reversed DP layout.

## Important APIs, Types, And Functions

`mcp89_sor_dp` supplies DP lane order `{3, 2, 1, 0}`, G94 link/power/pattern/drive/audio-symbol/active-symbol/watermark callbacks, and GT215 DP audio. `mcp89_sor` adds `g94_sor_state`, NV50 power/clock, GT215 backlight/HDMI/HDA, and the MCP89 DP table. `mcp89_sor_new()` creates HDA-capable SORs. `mcp89_disp` binds NV50 display lifecycle helpers with GT214 root/user classes.

## Control Flow

`mcp89_disp_new()` constructs the display engine with `mcp89_disp`. Shared NV50 oneinit enumerates display resources and invokes `mcp89_sor_new()` for each SOR. Later modesets execute through NV50 supervisor code but call MCP89's SOR DP/HDMI/HDA hooks when output methods request audio, link training, or backlight updates.

## State And Persistence Behavior

The file contributes static method tables only. Runtime state is stored in the generic display object graph, especially each SOR's `hda` flag and DP lane mapping in the function table.

## Dependencies And Integration Points

It depends on NV50 display core, G94 SOR DP helpers, GT215 backlight/HDMI/HDA helpers, and GT214/G84 class descriptors used by the NVIF client channel path.

## Risks And Edge Cases

The lane reversal is hardware-specific and affects DP training. Accidentally sharing the MCP77 table would break HDA audio and possibly DP lane ordering. Class IDs must align with userspace's expected GT214 display classes.

## Test Signals

Test signals include DP link training across all lane counts, HDA ELD/HPD changes through output methods, HDMI infoframe/audio behavior, and successful creation of GT214 display channel objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp89.c -->
