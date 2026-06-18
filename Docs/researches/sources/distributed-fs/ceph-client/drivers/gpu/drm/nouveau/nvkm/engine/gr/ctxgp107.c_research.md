# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgp107.c

`ctxgp107.c` is the Pascal GP107 context descriptor. Like GP104, it reuses GP102/GP100 helper logic and adjusts only resource limits for the smaller chip.

The sole export is `const struct gf100_grctx_func gp107_grctx`. It references GP102 attribute helpers, GP100 pagepool/attrib-CB/SMID helpers, GM107 bundle and SM-ID helpers, and GM200/GK104/GF117 topology helpers.

Generation is inherited. GP107 sets bundle token limit `0x300`, pagepool size `0x20000`, `attrib_nr_max` `0x15de`, `attrib_nr` `0x540`, alpha max/count `0xc00`/`0x800`, and `gfxp_nr` `0xe94`. Those constants feed the GP102 attribute-buffer size and per-PPC layout logic.

The file depends on `ctxgf100.h` and the Pascal/Maxwell helper stack. It integrates with GP107 device initialization as a constants-only variant.

Risks are attribute-buffer sizing and token limit mismatches on small Pascal GPUs. Test signals include GP107 boot, channel creation, OpenGL workloads, context-switch stress, and absence of attribute/pagepool memory faults.
