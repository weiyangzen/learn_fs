# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/mcp89.c

## Purpose
Defines MCP89 devinit behavior by reusing NV50 init/post paths, GT215 VPLL programming, and MCP89-specific engine disable mapping.

## Important APIs, types, and functions
Exports `mcp89_devinit_new()` and static `mcp89_devinit_disable()`.

## Control flow
Constructor delegates to `nv50_devinit_new_()`. Disable reads `0x001540/0x00154c` and disables MSPDEC, MSPPP, display, MSVLD, VIC, and copy engines as indicated.

## State and persistence
No extra software state. Persistent effects are standard NV50 init-script state, GT215 VPLL programming, and disabled engines.

## Dependencies and integration points
Depends on NV50 devinit helpers, GT215 PLL programming, BIOS init execution, and engine disable support.

## Risks
MCP89 has integrated chipset-specific media/VIC mappings; wrong bits could disable required display/media blocks.

## Test signals
MCP89 boot/display mode setting, media engine detection, post execution, and resume behavior.
