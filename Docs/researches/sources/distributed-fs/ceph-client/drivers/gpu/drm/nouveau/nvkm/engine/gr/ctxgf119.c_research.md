# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf119.c

`ctxgf119.c` supplies the GF119 late-Fermi context register packs. It extends GF108/GF110 initialization with expanded internal-command coverage, a GF119-specific `0x90c0` method pack, updated front-end, hub, GPC, TPC, texture, MPC, and SM defaults, and the `gf119_grctx` function table.

The exported object is `const struct gf100_grctx_func gf119_grctx`. Exported packs and tables include `gf119_grctx_pack_icmd`, `gf119_grctx_pack_mthd`, `gf119_grctx_init_fe_0`, `gf119_grctx_init_be_0`, `gf119_grctx_init_prop_0`, `gf119_grctx_init_gpc_unk_1`, `gf119_grctx_init_crstr_0`, and `gf119_grctx_init_sm_0`, many of which are reused by GF117 and Kepler files.

There is no custom generator logic. `gf100_grctx_generate_main()` consumes the static packs, then invokes inherited GF108/GF100 callbacks for unknown MMIO setup, bundle/pagepool allocation, attributes, SM IDs, TPC counts, ROP mapping, alpha/beta tables, eviction settings, and `0x419cb8`. The state is persistent only as static register-init data and callback constants.

The file depends on `ctxgf100.h` and sibling Fermi table exports. It integrates into Nouveau by providing the GR context function for GF119-family devices and by exporting common pack fragments for later chips. Method pack class IDs cover `0x9097`, `0x9197`, `0x9297`, `0x902d`, `0x9039`, and `0x90c0`.

The main risk is accidental breakage of exported tables used outside GF119. Small register defaults in FE/BE/GPC/TPC/SM packs can affect only some chipsets or graphics classes. Test signals are GF119 and GF117 boot/channel tests, class method initialization tests, OpenGL workloads with context switching, and absence of PGRAPH traps after suspend/resume.
