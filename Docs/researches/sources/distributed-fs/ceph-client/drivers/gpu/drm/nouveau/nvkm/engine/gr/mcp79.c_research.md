
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/mcp79.c

Purpose: MCP79 graphics-engine descriptor for NV50-family integrated chipsets. It does not implement new control flow; it binds the common `nv50_gr_init`, `nv50_gr_intr`, `nv50_gr_chan_new`, and `nv50_gr_units` hooks into a chip-specific `nvkm_gr_func`.

Important APIs/types/functions: `mcp79_gr_new()` calls `nv50_gr_new_()`. The static `mcp79_gr` function table exposes object classes `NV_NULL_CLASS`, `NV50_TWOD`, `NV50_MEMORY_TO_MEMORY_FORMAT`, `NV50_COMPUTE`, and `GT200_TESLA`, all using `nv50_gr_object`.

Control flow/state: creation is constructor-only: allocate/initialize common NV50 GR state in `nv50_gr_new_()`, then runtime state is managed by shared NV50 context and interrupt code. No persistent state is local to this file.

Dependencies/integration: depends on `nv50.h` and `nvif/class.h`; selected from chipset dispatch elsewhere in Nouveau. Risks are class-table omissions or wrong class IDs, which would surface as userspace channel/object creation failures. Test signals are successful engine probe, object allocation for the listed classes, and NV50 interrupt/init tests on MCP79 hardware.
