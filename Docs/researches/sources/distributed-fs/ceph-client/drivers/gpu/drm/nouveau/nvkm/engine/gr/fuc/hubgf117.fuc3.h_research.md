# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgf117.fuc3.h

Purpose: this header embeds GF117 FECS/hub FUC3 firmware. It provides `gf117_grhub_data[]` and `gf117_grhub_code[]` for global graphics context-control sequencing on GF117-family hardware.

Important APIs/types/functions: the static arrays are included by `gf117.c` and wrapped in `static struct gf100_gr_ucode gf117_gr_fecs_ucode`. Labels cover queue operations, register read/write waits, MMIO context transfer, strand initialization, firmware `init`, `init_gpc`, wait/main loops, channel-switch branches, interrupt handling, `ctx_4160s`, `ctx_4160c`, `ctx_4170s`, `ctx_4170w`, context memory load/wait, channel context load, MMIO execution, and xfer pre/exec/post/done.

Control flow: FECS initializes hub state and GPC firmware, then idles until channel-switch or firmware-method work arrives. On context switch, it evaluates previous/next channel cases, saves and loads channel data, executes MMIO lists, coordinates xfer with GPCCS images, and returns to the main loop or interrupt handler as needed.

State and persistence: `gf117_grhub_data[]` uses the standard hub layout: hub MMIO list offsets at `0x300/0x304`, `gpc_count`, `rop_count`, command queue, `ctx_current`, `chan_data`, `xfer_data`, and `hub_mmio_list_base`. The live state persists in FECS data memory and tracks current channel plus transfer bookkeeping.

Dependencies and integration points: this file pairs with `gpcgf117.fuc3.h`, is selected by GF117 GR setup, and uses the GF100 ucode loading ABI. It must match the GPCCS command protocol and the kernel's channel context layout.

Risks: the image is a hardware firmware blob, so compile-time type checking only verifies array syntax. Context-switch regressions can appear as FECS timeouts, GPC barrier stalls, or corrupted channel state. The retained `ctx_4160*` labels indicate GF117 still follows the GF100-style hub handler map, so later Kepler assumptions are not automatically valid.

Test signals: GF117 hardware should complete FECS/GPCCS startup, initialize GPCs, perform channel save/load transitions, handle interrupts, and run repeated 2D/3D workloads without context-control errors or xfer stalls.
