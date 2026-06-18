# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf117.c

`ctxgf117.c` defines the GF117 context layout, bridging late Fermi register packs with Kepler-style PPC-aware topology handling. It introduces PPC pack handling, ROP/tile mapping tailored to GF117, and per-PPC attribute allocation.

The primary export is `const struct gf100_grctx_func gf117_grctx`. Reused exports include `gf117_grctx_pack_gpc_1`, `gf117_grctx_init_pe_0`, and `gf117_grctx_init_wwdx_0`. Important functions are `gf117_grctx_generate_dist_skip_table()`, `gf117_grctx_generate_rop_mapping()`, and `gf117_grctx_generate_attrib()`.

The common main generator applies GF117 hub, GPC, TPC, PPC, internal command, and method packs. `gf117_grctx_generate_attrib()` iterates GPCs and PPCs, skips disabled PPCs through `gr->ppc_mask`, scales alpha/beta allocation by `gr->ppc_tpc_nr[gpc][ppc]`, and patches PPC-local registers. `gf117_grctx_generate_rop_mapping()` packs `gr->tile[]`, `gr->tpc_total`, and `gr->screen_tile_row_offset` into broadcast, TP broadcast, and `UNK78xx` mapping registers. `gf117_grctx_generate_dist_skip_table()` clears eight distribution skip registers.

The file depends on `ctxgf100.h`, `subdev/fb.h`, `subdev/mc.h`, and sibling GF108/GF119/GF104 tables. It integrates with chip functions that expose PPC topology through `gr->func->ppc_nr`, `ppc_mask`, `ppc_tpc_nr`, and `ppc_tpc_mask`. Later Kepler and Maxwell files reuse its ROP mapping and PPC attribute model.

Topology-derived state is the main risk. Incorrect PPC masks, tile packing, or alpha/beta offsets can corrupt attribute buffers or produce invalid ROP routing on partially fused chips. Test signals include GF117 hardware with asymmetric TPC/PPC configurations, repeated channel context switches, rendering tests that stress ROP/tile paths, and kernel logs for GR context or MMIO faults.
