# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp100.c

`ctxgp100.c` implements Pascal GP100 context-generation differences: new pagepool programming, GP100 attribute layout, attribute-buffer sizing, and an expanded SMID map format. It exports `gp100_grctx`.

Important functions are `gp100_grctx_generate_pagepool()`, the local `gp100_grctx_generate_attrib()`, `gp100_grctx_generate_attrib_cb()`, `gp100_grctx_generate_attrib_cb_size()`, and `gp100_grctx_generate_smid_config()`. The exported callback table is `const struct gf100_grctx_func gp100_grctx`.

`gp100_grctx_generate_pagepool()` patches pagepool base and control into `0x40800c/0x408010` and `0x419004/0x419008`. `gp100_grctx_generate_attrib()` separates attribute and alpha count registers (`0x405830`, `0x40585c`), lays out alpha first then attrib regions, allocates attrib space by `attrib_nr_max * ppc_tpc_max`, and clears `0x418eec` and `0x41befc`. `gp100_grctx_generate_attrib_cb_size()` computes the backing buffer size from alpha plus all PPC-max attrib regions, aligned to 128 bytes. `gp100_grctx_generate_smid_config()` writes distribution and per-GPC/TPC-group SM maps.

The file depends on `ctxgf100.h`, `subdev/fb.h`, and GM107/GM200/GK104/GF117 helpers. It is the base for GP102/GP104/GP107 and shares its pagepool and SMID logic with those variants.

Risks are buffer-size underestimation, address alignment, PPC-max versus active-TPC accounting, and SMID map indexing. Test signals include GP100 channel creation, multiple fused topology cases, Pascal shader workloads, context-switch stress, and pagepool/attribute buffer fault absence.
