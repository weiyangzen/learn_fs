# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgm107.fuc5.h

Purpose: this header embeds GM107 Maxwell GPCCS FUC5 firmware. It supplies `gm107_grgpc_data[]` and `gm107_grgpc_code[]`, adding Maxwell-specific TPC strand initialization to the GPC-side context-control firmware path.

Important APIs/types/functions: the C interface is the two static arrays included by `gm107.c` and wrapped as `static struct gf100_gr_ucode gm107_gr_gpccs_ucode`. Labels identify queue and MMIO helpers, `mmctx_*` transfer routines, strand helpers, `tpc_strand_wait`, `tpc_strand_busy`, `init`, `init_unk_loop`, `tpc_strand_init_tpc_loop`, `tpc_strand_init_idx_loop`, wait/main loops, interrupt handling, `hub_barrier_done`, redswitch handling, and context-transfer completion.

Control flow: the first half mirrors GK208-style FUC5 GPCCS firmware, but GM107 adds explicit TPC strand wait/busy and nested TPC strand initialization loops before normal runtime handling. During operation it waits for hub commands, transfers context state, coordinates barriers, handles redswitch delay, and completes load/save transfer paths.

State and persistence: `gm107_grgpc_data[]` uses the `0x6c` layout with GPC/TPC/unknown MMIO list offsets, topology counts/masks, and command queue storage. Runtime mutations happen in GPCCS data memory. The longer code array and extra labels are persistent evidence that GM107 needs more per-TPC setup than GK208.

Dependencies and integration points: `gm107.c` includes this file after `hubgm107.fuc5.h`, using the shared `struct gf100_gr_ucode` loader. This requested subset includes the GPC file but not its matching hub file; integration still depends on the paired GM107 FECS image and GM107 GR initialization sequence.

Risks: Maxwell-specific TPC strand loops make topology handling sensitive. A mismatch between `tpc_count`/`tpc_mask`, firmware expectations, and kernel GR topology discovery can hang initialization or leave TPC context strands uninitialized. As with all firmware blobs, code-word edits have no compile-time semantic checks.

Test signals: GM107 hardware should complete GPCCS firmware init, including TPC strand loops, and then survive repeated channel switches and graphics/compute workloads without GPCCS busy waits, barrier stalls, or per-TPC rendering faults.
