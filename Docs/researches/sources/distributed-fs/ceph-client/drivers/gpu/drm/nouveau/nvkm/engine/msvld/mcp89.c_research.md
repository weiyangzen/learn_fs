
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/mcp89.c

Purpose: MCP89 MSVLD descriptor for integrated GT21x-era hardware.

Important APIs/types/functions: `mcp89_msvld_new()` delegates to `nvkm_msvld_new_()` with `g98_msvld_init` and exposes `GT212_MSVLD`.

Control flow/state: no local mutable state; common Falcon construction and G98 initialization are reused.

Dependencies/integration: depends on `priv.h`, `nvif/class.h`, and G98 init helper. Risks are MCP89-specific init differences not reflected by reuse. Test signals are MCP89 MSVLD probe, Falcon init, and video decode class creation.
