# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm107.c

`ctxgm107.c` implements Maxwell GM107 context generation. It provides Maxwell register packs and changes attribute, bundle, pagepool, attribute-buffer, and SM-ID programming from the Kepler model.

The primary export is `const struct gf100_grctx_func gm107_grctx`. Important helpers are `gm107_grctx_generate_bundle()`, `gm107_grctx_generate_pagepool()`, `gm107_grctx_generate_attrib()`, `gm107_grctx_generate_attrib_cb()`, `gm107_grctx_generate_sm_id()`, and local hooks for `r406500` and `r419e00`. Exported reusable tables include `gm107_grctx_init_gpc_unk_0` and `gm107_grctx_init_wwdx_0`.

The common main generator consumes GM107 ICMD, method, hub, GPC, TPC, and PPC packs. `gm107_grctx_generate_bundle()` patches bundle addresses into both SCC and GPC paths (`0x408004/0x408008` and `0x418e24/0x418e28`) and writes token/FIFO limits. `gm107_grctx_generate_attrib()` lays out alpha/attrib regions per PPC, patches PPC base and size registers, and writes per-PPC usage registers at `0x418ea0 + n * 4`. `gm107_grctx_generate_attrib_cb()` calls the GF100 implementation and patches `0x419c2c` with the buffer address. `gm107_grctx_generate_sm_id()` writes SM IDs to three per-TPC/GPC locations.

The file depends on `ctxgf100.h`, `subdev/fb.h`, `subdev/mc.h`, and reusable GK104/GK110/GK208/GF117 helpers. It is the base for GM200/GM20B and later Pascal helpers. It integrates with topology fields such as `ppc_tpc_nr`, `ppc_tpc_max`, `tpc_total`, and SM numbering.

Risks include attribute buffer sizing and address patching, Maxwell-specific bundle paths, and SM ID writes that differ from Kepler. Test signals include GM107 hardware boot, multi-context OpenGL, fused topology coverage, pagepool/bundle address validation, and shader workloads sensitive to SM ID or attribute state.
