
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/mcp89.c

Purpose: MCP89 graphics-engine descriptor for a later NV50/GT21x integrated chipset. It reuses the common NV50 engine implementation while adding the MCP89 class exposure and TLB flush behavior.

Important APIs/types/functions: `mcp89_gr_new()` delegates to `nv50_gr_new_()`. `mcp89_gr` uses `nv50_gr_init`, `nv50_gr_intr`, `nv50_gr_chan_new`, `g84_gr_tlb_flush`, and `nv50_gr_units`. Supported classes include `NV50_COMPUTE`, `GT214_COMPUTE`, and `GT21A_TESLA`.

Control flow/state: no local mutable state; all state is owned by `struct nv50_gr` and the shared GR engine. The `tlb_flush` hook is the only behavior difference from MCP79 and integrates with VM/cache maintenance.

Dependencies/integration: depends on `nv50.h`, `nvif/class.h`, and the G84 flush helper declared through NV50 headers. Risks are stale translations if `g84_gr_tlb_flush` is wrong for this chipset, or class exposure mismatches. Test signals include VM fault-free channel execution after buffer remaps and successful object creation for GT214/GT21A classes.
