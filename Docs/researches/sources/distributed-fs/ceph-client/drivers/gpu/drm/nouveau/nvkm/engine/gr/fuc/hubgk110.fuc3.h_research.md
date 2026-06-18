# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk110.fuc3.h

Purpose: this header embeds GK110 FECS/hub FUC3 firmware. It supplies `gk110_grhub_data[]` and `gk110_grhub_code[]`, the hub-side context-control image for GK110 graphics hardware.

Important APIs/types/functions: the static arrays are included by `gk110.c` and exposed as `struct gf100_gr_ucode gk110_gr_fecs_ucode`. Firmware labels cover queue helpers, MMIO read/write/wait helpers, MMIO context transfer, strand setup, `init`, `init_gpc`, wait/main, channel-switch branches, interrupt paths, `ctx_4170s`, `ctx_4170w`, redswitch delay, context memory load, channel load, MMIO execution, and xfer execution/post/done.

Control flow: FECS initializes, starts GPC firmware, idles in its wait/main loop, processes channel-switch decisions, saves/loads context memory, executes hub MMIO lists, coordinates xfer with GPCCS, and completes context-transfer state. Its label topology matches GK104 closely and lacks the GF100/GF117 `ctx_4160*` labels.

State and persistence: `gk110_grhub_data[]` uses hub list offsets `0x300/0x304`, GPC/ROP count fields, command queue storage, current context tracking, channel data, xfer data, and the hub MMIO list base. Live state persists in FECS data memory between channel switches.

Dependencies and integration points: it pairs with `gpcgk110.fuc3.h` and the GK110 GR implementation. The shared loader consumes it through `struct gf100_gr_ucode`; FECS/GPCCS queue and barrier contracts must match.

Risks: the file is binary firmware represented as C array initializers. Word-level corruption, wrong array binding, or mismatched GPCCS firmware can cause GR init failure, FECS deadlocks, incorrect current-channel tracking, or corrupted save/load contexts. Similarity to GK104 should not hide chip-specific binary differences.

Test signals: successful GK110 FECS/GPCCS firmware load, GPC startup, context switch stability, correct behavior on fused-unit variants, and absence of FECS watchdog, interrupt-handler error, or xfer timeout messages under graphics stress.
