# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk110.c

`ctxgk110.c` adapts the GK104 Kepler context system for GK110. It provides GK110 internal-command and method packs, hub/GPC/TPC/PPC register defaults, and a few register workarounds for SM behavior.

The main export is `const struct gf100_grctx_func gk110_grctx`. Reusable exports include `gk110_grctx_pack_icmd`, `gk110_grctx_pack_mthd`, `gk110_grctx_init_pri_0`, `gk110_grctx_init_cwd_0`, `gk110_grctx_pack_hub`, `gk110_grctx_init_gpc_unk_2`, `gk110_grctx_pack_gpc_0`, `gk110_grctx_pack_gpc_1`, `gk110_grctx_init_tex_0`, `gk110_grctx_init_mpc_0`, `gk110_grctx_init_l1c_0`, and `gk110_grctx_pack_ppc`. Functions `gk110_grctx_generate_r419eb0()` and `gk110_grctx_generate_r419f78()` patch live SM registers.

Generation uses `gf100_grctx_generate_main()`, GK110 static packs, GK104 bundle/pagepool/LTC/topology helpers, and GF117 PPC attribute handling. The GK110 table changes bundle token limit to `0x7c0`, keeps the `0x3000` bundle size and `0x8000` pagepool, and adds `r419eb0`/`r419f78` hooks. `gk110_grctx_generate_r419eb0()` sets bit `0x1000`; `gk110_grctx_generate_r419f78()` clears bit 3 to keep loads enabled in FP helper invocations.

The file depends on `ctxgf100.h` plus GK104 and GF117 helper exports. It is itself a base for GK110B and GK208 variants. It integrates with class `0xa197` method initialization and Nouveau GR engine setup for GK110 devices.

Risks are GK110-specific register deltas, especially SM/L1C/MPC values and token limits. Incorrect `0x419f78` handling can affect shader helper invocation semantics. Test signals include GK110 OpenGL/compute rendering, multi-context stress, fused topology tests, and shader workloads that exercise helper loads and SM state restore.
