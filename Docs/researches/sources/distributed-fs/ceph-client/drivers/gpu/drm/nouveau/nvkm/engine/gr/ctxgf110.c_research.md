# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf110.c

`ctxgf110.c` adapts the GF100/GF108 context model for GF110-class Fermi GPUs. It provides a GF110 internal-command pack, class method overrides, a small GPC setup override, and the exported `gf110_grctx` function table.

The exported API is `const struct gf100_grctx_func gf110_grctx`, plus reusable method init tables `gf110_grctx_init_9197_0` and `gf110_grctx_init_9297_0`. The file defines `gf110_grctx_pack_icmd`, `gf110_grctx_pack_mthd`, and `gf110_grctx_pack_gpc_0`; it inherits most hub/GPC/TPC behavior from `gf100` and method class `0x9097` from `gf108_grctx_init_9097_0`.

Runtime generation is delegated to `gf100_grctx_generate_main()`. That generator consumes the GF110 packs, then runs inherited callbacks for bundle, pagepool, attributes, SM ID, TPC count, ROP mapping, alpha/beta tables, cache eviction settings, and register `0x419cb8`. There is no custom executable generator in this file; persistence is entirely in static register lists and the constants embedded in `gf110_grctx`.

The file depends on `ctxgf100.h` and sibling exports from GF100/GF108. It is part of the Nouveau `nvkm/engine/gr` family selected by GF110 device initialization. It must remain synchronized with method class IDs `0x9097`, `0x9197`, `0x9297`, `0x902d`, `0x9039`, and `0x90c0` because those class packs define the initial channel-visible method state.

Risks center on small per-chip deltas: the `0x9297` class block, `0x418830`, and `0x4188fc` setup values differ from related chips and can quietly break context restore. Test signals are GF110 channel bring-up, multi-context 3D workloads, method class initialization coverage, and absence of PGRAPH context faults during repeated context switches.
