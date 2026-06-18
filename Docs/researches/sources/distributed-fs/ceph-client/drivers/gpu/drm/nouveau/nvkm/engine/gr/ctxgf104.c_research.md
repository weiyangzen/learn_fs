# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf104.c

Purpose: defines GF104 graphics context differences from GF100, focused on TPC/TEX/L1C/SM init lists and a context function table that otherwise reuses the GF100 generator.

Important APIs and data: `gf104_grctx_init_tex_0`, `gf104_grctx_init_l1c_0`, `gf104_grctx_init_sm_0`, private `gf104_grctx_pack_tpc`, and exported `gf104_grctx`.

Control flow: `gf104_grctx` selects `gf100_grctx_generate_main()` and the standard GF100 hub/GPC/ZCULL/ICMD/MTHD packs, but swaps the TPC pack to use GF104 TEX/L1C/SM register values. Buffer generation, floorsweeping, ROP mapping, alpha/beta tables, and late hooks are inherited.

State and persistence: generated graphics context images include GF104-specific TPC register defaults. No independent runtime state exists in this file.

Dependencies and integration: depends on `ctxgf100.h`, GF100 shared init packs and helper functions, and the GF104 GR engine selecting this table.

Risks: only selected TPC blocks differ; if GF104 hardware requires other deviations they would be missed. Register-list mistakes can show up as graphics faults or context-switch failures rather than compile errors.

Test signals: GF104 context generation, TPC init list application, stable graphics workloads, context switch success, and absence of FECS/golden context timeout.
