# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgf117.fuc3.h

Purpose: this header embeds GF117 GPCCS firmware for GPC-side graphics context control. It supplies `gf117_grgpc_data[]` and `gf117_grgpc_code[]` for the GF117 GR driver, covering command queues, MMIO context movement, strand initialization, interrupt handling, and GPC-to-hub synchronization.

Important APIs/types/functions: the C-visible contract is the two static arrays, included by `gf117.c` and wrapped in `static struct gf100_gr_ucode gf117_gr_gpccs_ucode`. Firmware label comments identify queue helpers, MMIO helpers, wait helpers, `mmctx_size`, `mmctx_xfer`, `strand_wait/pre/post/set`, `strand_ctx_init`, `init`, `init_unk_loop`, `main`, `ih`, `ih_no_fifo`, `hub_barrier_done`, `ctx_redswitch`, and `ctx_xfer`.

Control flow: compared with GF100, GF117 adds explicit unknown-unit count/mask state and an `init_unk_loop/init_unk_next/init_unk_done` sequence before the main wait loop. The runtime path receives work from FECS/hub firmware via the command queue, services context-transfer requests, waits for MMIO/strand readiness, posts barrier completion back to the hub, and returns to its wait/main loop.

State and persistence: `gf117_grgpc_data[]` uses a `0x6c` list base and includes `gpc_id`, `tpc_count`, `tpc_mask`, `unk_count`, `unk_mask`, and an 18-word command queue at `0x0024`. These offsets are part of the firmware ABI with the kernel-side GR loader and the hub firmware. The arrays are built into the driver and loaded into GPCCS instruction/data memory during GR initialization.

Dependencies and integration points: `gf117.c` includes this file after `hubgf117.fuc3.h`, then binds it as the GPCCS ucode image. It relies on the GF100-era context-control loader and coordinates with FECS hub firmware for channel switching and GPC-local state transfers.

Risks: the word stream is not self-validating at compile time. Data-layout drift from the kernel loader, queue offset mistakes, or mismatched FECS/GPCCS firmware can hang context switches. The additional unknown-unit loop is particularly sensitive because it likely tracks hardware units not present in GF100.

Test signals: GF117-class boards should boot GR firmware, initialize all GPC/TPC/unknown unit masks, run channel switches, and sustain graphics workloads without FECS/GPCCS timeouts, hub barrier stalls, or context image corruption.
