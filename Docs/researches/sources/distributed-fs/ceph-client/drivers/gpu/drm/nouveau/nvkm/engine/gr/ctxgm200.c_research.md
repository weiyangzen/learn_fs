# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm200.c

`ctxgm200.c` defines high-level GM200 Maxwell context behavior by reusing GM107 generators and adding GM200-specific topology and register hooks. It contains no static register packs.

The main export is `const struct gf100_grctx_func gm200_grctx`. Important functions are `gm200_grctx_generate_r419a3c()`, `gm200_grctx_generate_smid_config()`, `gm200_grctx_generate_tpc_mask()`, `gm200_grctx_generate_r406500()`, `gm200_grctx_generate_dist_skip_table()`, and the local `gm200_grctx_generate_r418e94()`.

The common main generator uses inherited GM107 bundle/pagepool/attribute callbacks, then invokes GM200 hooks. `gm200_grctx_generate_smid_config()` builds a compact SM distribution table at `0x405b60` and per-GPC SM maps at `0x405ba0`. `gm200_grctx_generate_tpc_mask()` writes enabled TPC masks to `0x4041c4`. `gm200_grctx_generate_dist_skip_table()` computes skip masks by removing the minimum active TPCs per PPC and writes eight `0x4064d0` registers. The table uses pagepool size `0x20000`, bundle token limit `0x780`, and smaller attrib counts than GM107.

The file depends on `ctxgf100.h` and GM107/GK104/GF117 helpers. It integrates with device topology fields `sm[]`, `sm_nr`, `gpc_nr`, `tpc_nr`, `ppc_tpc_nr`, `ppc_tpc_mask`, and `ppc_tpc_min`.

Risks are topology packing mistakes in SMID and skip tables, incorrect TPC masks on fused chips, and register hooks with full-register masks. Test signals include GM200 cards with non-uniform TPC layouts, channel switches, shader scheduling tests, and kernel logs for context or SM mapping errors.
