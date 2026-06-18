# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dsi.c

Purpose: Unisoc MIPI DSI host, D-PHY control, DRM encoder, panel bridge, and MIPI DSI host operations.

Important APIs and types: `struct sprd_dsi` contains `mipi_dsi_host`, optional slave, DRM encoder, panel bridge, and `dsi_context`. Register helpers modify MMIO fields. `regmap_tst_io_*()` exposes the PHY test interface as an 8-bit regmap for PLL code. Host ops implement attach/detach/transfer. Encoder helpers initialize video/cmd mode, DPHY, and DPU coordination.

Control flow: platform probe allocates `sprd_dsi` and registers a MIPI DSI host. A panel attaches as `slave`, setting work mode and burst mode, then component-add triggers DRM bind. Bind initializes encoder, attaches panel bridge from OF graph port 1, and maps DSI/PHY resources. Encoder enable initializes host registers, configures DPI or EDPI packet timing, initializes DPHY PLL/timing, switches work mode, resets controller state, configures clock lane mode, starts the DPU, and marks enabled. Disable stops DPU, tears down DPHY and host. Host transfer sends generic/DCS packets or reads using FIFO polling.

State and persistence: `dsi_context` stores MMIO base, PHY regmap, PLL fields, videomode, enabled flag, work/burst mode, interrupt masks, timing constants, max read time, and TE/frame ACK options. Attached slave stores lanes, format, rates, and mode flags.

Dependencies and integration: depends on component framework, DRM bridge/panel/OF helpers, MIPI DSI host API, DPU public run/stop functions, and `megacores_pll.c`.

Risks: `sprd_dsi_context_init()` initializes `ctx->enabled = true`, so the first encoder enable will warn and return without programming hardware unless another path clears it; this is a notable behavioral risk. `dphy_pll_config()` return is ignored in `sprd_dphy_init()`. Video packet range programming often uses sizes relative to zero and may mishandle nonzero offsets if ever introduced. FIFO polling is busy-wait based. Host transfer returns 0 for empty messages and count for reads, but write transfers return only 0 or error rather than transmitted length.

Test signals: attach/detach component sequencing, first enable behavior, video and command mode panels, burst/non-burst calculations, PLL lock timeout, read/write packet transfers, continuous and non-continuous clock modes, and bridge removal.
