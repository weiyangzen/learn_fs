# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk110b.c

`ctxgk110b.c` is a narrow GK110B revision override. It reuses GK110 context generation almost entirely but replaces the SM init table and TPC pack, then exports `gk110b_grctx`.

The main export is `const struct gf100_grctx_func gk110b_grctx`. The only local static data is `gk110b_grctx_init_sm_0` and `gk110b_grctx_pack_tpc`, which combine GF117 PE, GK110 TEX/MPC/L1C, and GK110B SM defaults.

There is no custom runtime function. `gf100_grctx_generate_main()` consumes GK110 hub, GPC, PPC, ICMD, and method packs plus the GK110B TPC pack. Bundle, pagepool, attributes, LTC patching, topology, ROP mapping, alpha/beta tables, and SM register workarounds come from GK104/GK110/GF117 helpers.

The file depends on `ctxgf100.h` and the GK110/GK104/GF117 exported helpers. It integrates as the context function selected by GK110B-class device descriptors.

Risk is concentrated in the SM defaults, especially `0x419f70`, `0x419f78`, and related SM context fields that differ from GK110. Test signals are GK110B boot, graphics channel creation, shader-heavy workloads, and comparison with GK110 behavior to catch revision-specific regressions.
