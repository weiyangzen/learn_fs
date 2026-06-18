# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxga102.c

Purpose: defines GA102/Ampere graphics context-generation parameters and a few GA102-specific patch functions on top of the GF100/GV100/TU102 context framework.

Important APIs and data: `ga102_grctx_generate_sm_id()` maps logical TPC through `gv100_gr_nonpes_aware_tpc()` and writes SM id at `TPC_UNIT(..., 0x608)`. `ga102_grctx_generate_unkn()` sets bits in `0x41980c` and `0x41be08`. `ga102_grctx_generate_r419ea8()` writes `0x419ea8` from `0x504728 | 0x08000000`. The exported `ga102_grctx` table selects buffer sizes, counts, and inherited generation hooks.

Control flow: the generic `gf100_grctx_generate_main()` calls the function-table hooks for bundle/pagepool/attribute buffers, unknown buffer, floorsweeping, ROP mapping, and late register patches. GA102 custom hooks run during those phases.

State and persistence: context data is generated into runtime graphics context images and patch buffers. The table defines bundle size `0x3000`, pagepool `0x20000`, attrib/alpha counts, unknown buffer size `0x80000`, and GFXP count `0xd28`.

Dependencies and integration: depends on `ctxgf100.h` declarations, inherited GM107/GP100/GP102/GV100/TU102/GM200 helpers, and GA102 GR engine code selecting this table.

Risks: register constants and count values are tightly hardware-specific; non-PES-aware TPC mapping would produce wrong SM ids; missing hub/GPC/TPC pack pointers means this table relies on inherited firmware or alternate paths in the broader GA102 GR code.

Test signals: GA102 context generation success, no FECS/golden context timeout, correct SM id programming on floorswept GPUs, valid attribute/bundle/pagepool sizes, and graphics workloads surviving context switches.
