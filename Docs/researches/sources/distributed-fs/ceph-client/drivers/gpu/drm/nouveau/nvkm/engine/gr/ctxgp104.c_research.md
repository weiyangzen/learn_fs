# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp104.c

`ctxgp104.c` is a compact Pascal GP104 context descriptor. It reuses GP102/GP100/GM107/GM200 helpers and only supplies GP104-specific resource constants in `gp104_grctx`.

The sole export is `const struct gf100_grctx_func gp104_grctx`. It references `gp102_grctx_generate_attrib_cb_size()`, `gp100_grctx_generate_attrib_cb()`, `gp102_grctx_generate_attrib()`, `gp100_grctx_generate_pagepool()`, `gm107_grctx_generate_bundle()`, `gp100_grctx_generate_smid_config()`, and GM200/GK104/GF117 topology hooks.

Runtime control flow is entirely inherited from `gf100_grctx_generate_main()` and the referenced helpers. GP104 uses bundle token limit `0x900`, pagepool size `0x20000`, `attrib_nr_max` `0x4b0`, `attrib_nr` `0x320`, alpha max/count `0xc00`/`0x800`, and `gfxp_nr` `0xba8`. It does not install GP102's `r408840` hook.

The file depends on `ctxgf100.h` and helper symbols from GP102, GP100, GM107, GM200, GK104, and GF117. It integrates with GP104 device descriptors as a constants-only context variant.

Risks are wrong constants for GP104 relative to GP102 or GP107, especially `gfxp_nr` and token limit. Test signals include GP104 hardware channel initialization, graphics workloads with context switching, and validation that GP102-only `r408840` behavior is not required.
