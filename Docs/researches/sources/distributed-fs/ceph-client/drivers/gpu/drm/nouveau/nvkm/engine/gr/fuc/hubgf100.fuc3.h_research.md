# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgf100.fuc3.h

Purpose: this header embeds GF100 FECS/hub FUC3 firmware for global graphics context control. It defines `gf100_grhub_data[]` and `gf100_grhub_code[]`, which orchestrate channel switches, hub MMIO context state, GPC initialization, channel context load/save, xfer execution, and interrupt handling.

Important APIs/types/functions: there are no C-callable routines. `gf100.c` includes the header and publishes it as `struct gf100_gr_ucode gf100_gr_fecs_ucode`. Firmware labels include queue helpers, MMIO helpers, `mmctx_size`, `mmctx_xfer`, strand helpers, `init`, `init_gpc`, `wait`, `main`, channel-switch branches (`chsw_prev_no_next`, `chsw_no_prev`, `chsw_done`), interrupt paths, context register handlers (`ctx_4160s`, `ctx_4160c`, `ctx_4170s`, `ctx_4170w`), memory load/wait, channel context load, MMIO execution loop, and xfer pre/exec/post/done.

Control flow: FECS initializes hub state, starts GPC firmware via `init_gpc`, waits for work, decides channel-switch cases, saves previous channel state, loads next channel state, executes MMIO list operations, coordinates xfer operations with GPC firmware, and handles firmware method/interrupt paths. Hub code owns global sequencing while GPCCS owns GPC-local execution.

State and persistence: `gf100_grhub_data[]` starts with hub MMIO list head/tail `0x300/0x304`, `gpc_count`, `rop_count`, an 18-word command queue, `ctx_current`, `chan_data` including channel MMIO count/address entries, `xfer_data`, and `hub_mmio_list_base`. FECS data memory stores current channel and transfer state across context switches after upload.

Dependencies and integration points: it pairs with `gpcgf100.fuc3.h` and is loaded by the GF100 GR context-control init path. It uses the same `struct gf100_gr_ucode` mechanism as later chips and must agree with GPCCS on command queues, barriers, and transfer layout.

Risks: FECS hub firmware is central to all channel switching. A wrong data offset or instruction word can prevent GR initialization, corrupt the current-channel pointer, deadlock waiting for GPCs, or mis-save channel context. GF100 includes `ctx_4160*` handlers that later GK104/GK110 hub images no longer label, so cross-family substitution is unsafe.

Test signals: GF100 boards should load FECS, start all GPC firmware, create and switch channels, save/load contexts, and run workloads without FECS interrupt storms, no-context-switch paths, xfer idle timeouts, or channel-state corruption.
