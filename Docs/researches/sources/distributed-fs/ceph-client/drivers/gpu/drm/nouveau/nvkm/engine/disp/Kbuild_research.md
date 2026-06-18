<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/Kbuild

Purpose: Kbuild fragment listing the Nouveau NVKM display engine objects that are linked into `nvkm-y`.

Important entries: common display components include `base.o`, `chan.o`, `conn.o`, `dp.o`, `hdmi.o`, `head.o`, `ior.o`, `outp.o`, and `vga.o`. Generation implementations span `nv04.o`, `nv50.o`, `g84.o`, `g94.o`, `gt200.o`, `mcp77.o`, `gt215.o`, `mcp89.o`, `gf119.o`, `gk104.o`, `gk110.o`, `gm107.o`, `gm200.o`, `gp100.o`, `gp102.o`, `gv100.o`, `tu102.o`, and `ga102.o`. User-facing display object wrappers are `udisp.o`, `uconn.o`, `uoutp.o`, and `uhead.o`.

Control flow: no runtime control flow. Build order ensures shared display infrastructure and generation-specific callback providers are compiled into the module.

State and persistence: none directly; it determines which display implementations are available at runtime.

Dependencies and integration points: integrates with the parent Nouveau Kbuild by appending to `nvkm-y`. The list mirrors constructors referenced from chip/device tables elsewhere in NVKM.

Risks: omitting an object produces link failures or missing constructor symbols for a GPU generation. Adding a generation source without updating this file prevents it from being built. Removing common objects breaks many generations.

Test signals: kernel/module build, symbol resolution for all display constructors, and probe of GPUs from each listed family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/Kbuild -->
