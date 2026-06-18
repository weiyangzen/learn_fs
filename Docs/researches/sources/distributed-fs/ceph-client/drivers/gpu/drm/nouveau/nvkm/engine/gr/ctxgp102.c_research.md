# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp102.c

`ctxgp102.c` defines Pascal GP102/large-Pascal context differences over GP100. It introduces GFXP-sized attribute regions, a GP102 attribute-buffer size calculation, and a `0x408840` register hook.

The exported object is `const struct gf100_grctx_func gp102_grctx`. Important functions are `gp102_grctx_generate_attrib()`, `gp102_grctx_generate_attrib_cb_size()`, and the local `gp102_grctx_generate_r408840()`.

`gp102_grctx_generate_attrib()` writes attribute, alpha, and max-batch registers, then walks active PPCs. It patches PPC `+0xc0` with `gfxp_nr * ppc_tpc_max`, writes per-GPC attribute size at `GPC_UNIT(gpc, 0xc44 + ppc * 4)`, manages attrib and alpha offsets, and writes per-PPC usage at `0x418ea0 + n * 4`. It also patches `0x4181e4` and `0x41befc` to `0x100`. The size helper sums alpha state plus `gfxp_nr * ppc_nr * ppc_tpc_max` for each GPC, aligned to 128 bytes.

The file depends on `ctxgf100.h`, `subdev/fb.h`, GP100 pagepool/attrib-CB/SMID helpers, GM107 bundle/SMID helpers, GM200 topology hooks, and GK104 unknown setup. GP104 and GP107 reuse these GP102 attribute helpers with different constants.

Risks include using `gfxp_nr` incorrectly, underallocating attribute buffers, and applying GP102-only `0x408840` behavior to the wrong chip. Test signals include GP102 rendering and context switching, shader workloads that stress GFXP state, fused topology coverage, and checks for context buffer overruns.
