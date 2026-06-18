# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk104.fuc3.h

Purpose: this header embeds GK104 FECS/hub FUC3 firmware for Kepler graphics context control. It defines `gk104_grhub_data[]` and `gk104_grhub_code[]`, the global firmware image that manages channel switching and coordinates GPC firmware.

Important APIs/types/functions: `gk104.c` includes this header and wraps the arrays in `static struct gf100_gr_ucode gk104_gr_fecs_ucode`. Labels include queue/MMIO helpers, `mmctx_size`, `mmctx_xfer`, strand helpers, `init`, `init_gpc`, wait/main loops, channel-switch branches, interrupt paths, `ctx_4170s`, `ctx_4170w`, `ctx_redswitch`, `ctx_86c`, `ctx_mem`, `ctx_load`, channel/MMIO execution, and xfer pre/exec/post/done.

Control flow: after initialization and GPC startup, the hub firmware waits for channel/context work, handles previous/next channel cases, executes memory and MMIO context operations, directs xfer work, waits for xfer idle, and finalizes channel context state. Relative to GF100/GF117 hub images, the labeled `ctx_4160s` and `ctx_4160c` handlers are absent and offsets shift accordingly.

State and persistence: `gk104_grhub_data[]` follows the standard hub data layout with `hub_mmio_list_head/tail`, `gpc_count`, `rop_count`, an 18-word command queue, `ctx_current`, `chan_data`, `xfer_data`, and `hub_mmio_list_base`. The firmware updates current-channel and transfer fields in FECS data memory.

Dependencies and integration points: it pairs with `gpcgk104.fuc3.h`, is loaded through the GF100 GR ucode path, and is selected by GK104 GR functions. It must remain in sync with GPCCS firmware and the GK104 channel/context layout.

Risks: Kepler FECS firmware is opaque and tightly coupled to hardware register semantics. Missing or altered words can hang `init_gpc`, break channel switching, or desynchronize MMIO/xfer operations. The absence of GF100-style `ctx_4160*` handlers is a family-specific distinction that matters when comparing blobs.

Test signals: GK104 cards should load hub and GPC firmware, initialize GPCs, create multiple channels, switch between them, and run GL/compute workloads without FECS errors, xfer idle waits, or context corruption.
