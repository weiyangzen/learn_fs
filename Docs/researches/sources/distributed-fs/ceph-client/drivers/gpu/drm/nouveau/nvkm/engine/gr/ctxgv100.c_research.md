# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgv100.c

`ctxgv100.c` implements Volta GV100 context-generation differences. It adds a software VEID bundle-init pack, Volta attribute layout and attribute-buffer programming, non-PES-aware SM ID mapping, wider ROP mapping, and several live MMIO hooks.

The exported object is `const struct gf100_grctx_func gv100_grctx`. Important APIs include `gv100_grctx_generate_attrib()`, `gv100_grctx_generate_attrib_cb()`, `gv100_grctx_generate_rop_mapping()`, `gv100_grctx_generate_r400088()`, `gv100_grctx_generate_unkn()`, `gv100_grctx_unkn88c()`, and the local `gv100_grctx_generate_sm_id()`. The file also defines `gv100_grctx_pack_sw_veid_bundle_init`.

The common main generator uses inherited bundle/pagepool and topology hooks plus GV100-specific callbacks. `gv100_grctx_generate_attrib()` follows GP102-style GFXP allocation but does not write the per-GPC `0xc44` register. `gv100_grctx_generate_attrib_cb()` patches the attribute buffer at `0x419e00/0x419e04`. `gv100_grctx_generate_rop_mapping()` writes tile maps to broadcast, TP broadcast, and `UNK78xx` registers using a map length derived from maximum GPC/TPC capacity and 5-bit tile values. `gv100_grctx_generate_sm_id()` converts TPC IDs with `gv100_gr_nonpes_aware_tpc()` before writing SM IDs. `unkn88c` toggles bit `0x10` in three registers with readbacks.

The file depends on `ctxgf100.h` plus GV100 GR topology helpers, GP102 sizing, GP100 pagepool/SMID logic, GM107 bundle/attrib base programming, and GM200 distribution hooks. It integrates with Volta context setup, including VEID bundle initialization absent from earlier chips.

Risks include non-PES TPC remapping, larger tile-map packing, VEID bundle-init correctness, and live MMIO toggles that can affect context isolation. Test signals include GV100 channel creation, context switching with multiple VEIDs where supported, shader workloads, fused topology mapping, and checking for GR faults around `0x40988c`, `0x41a88c`, or ROP map registers.
