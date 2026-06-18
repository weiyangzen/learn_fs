# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk208.c

`ctxgk208.c` defines the context register packs and callback table for GK208 Kepler GPUs. It mixes GK110/GK104 infrastructure with GK208-specific ICMD, FE, hub, GPC, TPC, PPC, texture, SM, and CBM defaults.

The exported object is `const struct gf100_grctx_func gk208_grctx`. Reusable exported tables include `gk208_grctx_init_rstr2d_0`, `gk208_grctx_init_prop_0`, `gk208_grctx_init_crstr_0`, and the local pack tables for ICMD, hub, GPC, TPC, and PPC. The function table reuses `gk104_grctx_generate_bundle()`, `gk104_grctx_generate_pagepool()`, `gf117_grctx_generate_attrib()`, `gk104_grctx_generate_patch_ltc()`, `gf117_grctx_generate_rop_mapping()`, and `gk110_grctx_generate_r419f78()`.

The common main generator applies GK208 static packs, then calls inherited topology and buffer callbacks. Important constants are bundle size `0x3000`, minimum GPM FIFO depth `0xc2`, token limit `0x200`, pagepool size `0x8000`, alpha count `0x648`, and `alpha_nr_max` `0x7ff`. The ICMD table is GK208-specific and includes additional `0x00c4xx`/`0x00c5xx` entries not present in earlier Kepler variants.

The file depends on `ctxgf100.h` and sibling GK104/GK110/GF117 table exports. It integrates with GK208 device GR setup and shares many helper callbacks with other Kepler chips, while providing lower token/FIFO limits appropriate to this smaller GPU.

Risks are mis-sized bundle limits, incorrect GK208-specific ICMD ranges, and mismatched inherited helpers on smaller fused topologies. Test signals include GK208 channel creation, desktop OpenGL workloads, suspend/resume, context switching between clients, and absence of PGRAPH traps involving `0x00c4xx` or SM state.
