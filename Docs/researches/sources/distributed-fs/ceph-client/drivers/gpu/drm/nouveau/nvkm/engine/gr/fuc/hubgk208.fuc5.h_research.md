# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk208.fuc5.h

Purpose: this header embeds GK208 FECS/hub firmware using the FUC5 instruction encoding. It defines `gk208_grhub_data[]` and `gk208_grhub_code[]` for hub-side graphics context control on GK208.

Important APIs/types/functions: `gk208.c` includes the header and wraps the arrays as `static struct gf100_gr_ucode gk208_gr_fecs_ucode`. Labels identify queue operations, MMIO helpers, context-size/transfer helpers, strand setup, `init`, `init_gpc`, wait/main loops, channel-switch branches, interrupt paths, `ctx_4170s`, `ctx_4170w`, redswitch handling, context memory load, channel load, MMIO loop, and xfer pre/exec/post/done.

Control flow: the firmware initializes hub state, starts GPC firmware, waits for channel-switch work, handles previous/next channel cases, saves/loads channel context, executes MMIO and xfer operations, and returns to the main loop. It is the FUC5 counterpart to the GK104/GK110 hub flow, with shorter code and shifted offsets.

State and persistence: `gk208_grhub_data[]` keeps hub MMIO list pointers at `0x300/0x304`, GPC/ROP counts, command queue, `ctx_current`, channel MMIO metadata, xfer metadata, and the hub MMIO list base. Runtime updates live in FECS data memory; the C arrays are the immutable load image.

Dependencies and integration points: it pairs with `gpcgk208.fuc5.h` and is selected by GK208 GR setup. The shared GF100 ucode wrapper provides code/data pointers and sizes to the firmware loader.

Risks: FUC5 opcodes are not interchangeable with FUC3 images. Any manual edit, bad size, or mismatched GPC image can break FECS startup, GPC init, xfer coordination, or channel context save/load. Family-specific label offsets should be treated as part of the firmware ABI.

Test signals: GK208 systems should complete FECS and GPCCS load, create channels, switch contexts repeatedly, and run rendering workloads without FECS/GPCCS timeouts, interrupt error paths, or context memory corruption.
