# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf100.h

Purpose: declares the GF100-family graphics context generation interface, function table, generation hooks, variant tables, and shared init-pack symbols.

Important APIs and data: `struct gf100_grctx_func` defines hooks for main generation, unknown setup, MMIO packs, indirect command/method packs, bundle/pagepool/attribute buffers, patch buffers, floorsweeping, SM/TPC/ROP/alpha/beta mapping, and many late register hooks. It declares `gf100_grctx_generate()`, shared GF100 helpers, and variant tables from GF108/GF104/GF110 through GA102.

Control flow: chip GR files select one `gf100_grctx_func` table. The generic generator calls callbacks in defined phases: MMIO pack load, buffer patching, floorsweeping, indirect bundle/method emission, and late register fixes.

State and persistence: no storage itself. It defines parameters and hooks that control generated graphics context images, patch buffers, and hardware register state.

Dependencies and integration: includes `gf100.h` and is used by all GF100-derived context generator C files. FIFO engine context binding ultimately consumes generated GR context objects through channel contexts.

Risks: broad declaration surface means incompatible signature or field changes affect many generations; optional hooks require careful null checks; table parameter mistakes can create invalid context images without compile-time detection.

Test signals: full build across all GR context files, variant table linkage, successful context generation on multiple generations, and no unresolved shared init-pack symbols.
