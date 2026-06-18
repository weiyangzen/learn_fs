# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgf100.c

Purpose: implements the GF100/Fermi graphics context generator and the baseline register-init packs used by many later GR context variants. It contains large MMIO/init lists, patch helpers, buffer setup, floorsweeping, ROP/alpha/beta mapping, FECS/golden context generation, and the exported `gf100_grctx` table.

Important APIs and data: exported symbols include `gf100_grctx_patch_wr32()`, `gf100_grctx_generate_main()`, `gf100_grctx_generate()`, `gf100_grctx_generate_bundle()`, `gf100_grctx_generate_pagepool()`, `gf100_grctx_generate_attrib_cb_size()`, `gf100_grctx_generate_attrib_cb()`, `gf100_grctx_generate_attrib()`, `gf100_grctx_generate_floorsweep()`, `gf100_grctx_generate_sm_id()`, `gf100_grctx_generate_tpc_nr()`, `gf100_grctx_generate_rop_mapping()`, `gf100_grctx_generate_alpha_beta_tables()`, and many `gf100_grctx_pack_*` / `gf100_grctx_init_*` lists.

Control flow: `gf100_grctx_generate()` forces FE power, resets FECS, allocates temporary context memory with a reserved prefix, maps it into the channel VMM, points the channel instance at it, makes the channel current either through firmware FECS bind or direct registers, runs `grctx->main()`, unloads/saves the golden context, copies generated context data into `gr->data`, and clears the instance pointer. `gf100_grctx_generate_main()` loads MMIO packs, waits idle, patches pagepool/bundle/attribute buffers, performs floorsweeping, loads indirect command and method bundles, restores timeouts, and applies late hooks.

State and persistence: generated context data is cached in `gr->data` for runtime use. Temporary `nvkm_memory` and VMA allocations are freed. Hardware state is programmed during generation and synchronized through idle waits.

Dependencies and integration: depends on GF100 GR private structures, FB/MC/timer helpers, FIFO context helpers, FECS firmware paths, and later variant tables declared in `ctxgf100.h`.

Risks: massive register tables are difficult to audit; missing alpha/beta maps fall back with warnings; FECS/golden-save timeouts can fail context generation; floorsweeping depends on accurate `gpc/tpc/sm/tile` topology; patch-buffer path changes behavior when `chan->mmio` is present.

Test signals: successful golden context generation, FECS bind/save completion, no idle wait timeouts, stable `gr->data` size, graphics context switch tests, warnings for missing alpha/beta mapping, and workloads on floorswept GPUs.
