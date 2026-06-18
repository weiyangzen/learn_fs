# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk104.fuc3.h

Purpose: this header embeds GK104 Kepler GPCCS firmware. It provides `gk104_grgpc_data[]` and `gk104_grgpc_code[]`, the GPC-side falcon data/code image used for context-state transfers, strand setup, GPC/TPC/unknown-unit initialization, and synchronization with hub FECS firmware.

Important APIs/types/functions: there are no callable C routines. `gk104.c` includes the header and wraps the arrays in `static struct gf100_gr_ucode gk104_gr_gpccs_ucode`. Comment labels expose the firmware routine map: queue operations, `nv_rd32`/`nv_wr32` waits, `mmctx_size`, `mmctx_xfer`, `strand_ctx_init`, `init_unk_loop`, `wait`, `main`, interrupt handler paths, `hub_barrier_done`, `ctx_redswitch`, and `ctx_xfer`.

Control flow: the label structure is the GF117-style FUC3 GPCCS flow with an unknown-unit init loop and context-transfer paths. Runtime execution waits for hub commands, pulls queue entries, performs MMIO or strand context movement, acknowledges hub barriers, handles redswitch delay, and finalizes transfer state through `ctx_xfer_post`/`ctx_xfer_done`.

State and persistence: `gk104_grgpc_data[]` has list heads/tails at `0x6c`, GPC identity/topology fields, `unk_count`, `unk_mask`, and an 18-entry command queue. This is persistent firmware data memory initialized by the driver and then updated by GPCCS during operation. The array sizes are consumed via `sizeof()` by the GR ucode wrapper.

Dependencies and integration points: it pairs with `hubgk104.fuc3.h` and the GK104 GR implementation. The hub firmware orchestrates global channel/context switching while this GPCCS image performs GPC-local work, so the command queue and barrier semantics must match between the two images.

Risks: although it resembles GF117/GK110 firmware, it is a chip-specific binary. Substituting another chip's words or changing offsets can break Kepler context switching in ways that only appear under multi-channel or per-GPC workloads. Since comments are labels only, source review cannot prove instruction correctness.

Test signals: GK104 boards should load GPCCS, initialize all enabled GPC/TPC resources, run graphics context switches, and avoid firmware error paths, hub barrier waits, and GR faults during 3D/compute stress.
