# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/dp/dp_hw.c

Purpose: implements the low-level HIBMC DisplayPort hardware programming layer. It owns DP transmitter initialization, interrupt masking, HPD setup, stream timing programming, link enable/disable, link-status reset, color-bar test generation, and simple accessors for negotiated link rate and lane count.

Important APIs and functions: `hibmc_dp_hw_init()` allocates and wires `struct hibmc_dp_dev`, initializes AUX, SERDES, default 2-lane HBR3-like caps, resets DPTX, programs HDCP and clock enable registers. `hibmc_dp_mode_set()` triggers link training if channel equalization is not already true, disables the stream, then calls `hibmc_dp_link_cfg()`. `hibmc_dp_display_en()` toggles video and GCTL stream bits with timing sync strobes. `hibmc_dp_set_cbar()` programs color bar or solid RGB test output from `g_rgb_raw`. `hibmc_dp_check_hpd_status()` polls HPD state for up to 100 ms.

Control flow: mode setup flows from DRM encoder enable in `hibmc_drm_dp.c` into `hibmc_dp_prepare()`, then `hibmc_dp_mode_set()`. Link training is delegated to `dp_link.c`; if successful, this file writes timing generator, MSA, TU, SST, polarity, video mapping, and sync delay fields to MMIO. Stream enable is separate and occurs after timing is programmed.

State and persistence: persistent runtime state is in `dp->dp_dev`: `link.cap`, `link.status`, `hpd_status`, MMIO bases, AUX pointer, and mutex. Hardware state persists in DPTX registers until reset or driver teardown. No disk persistence exists.

Dependencies and integration points: depends on `dp_comm.h` register helpers, `dp_config.h` constants, `dp_reg.h` offsets, DRM display mode fields, Linux `readl_poll_timeout()`, and SERDES/link-training functions. It is integrated by `hibmc_dp_init()`, the HPD ISR, debugfs colorbar control, and connector mode validation.

Risks: TU/SST math assumes nonzero lane count and supported bpp/rate constants. `hibmc_dp_set_cbar()` indexes `g_rgb_raw` by pattern after validation in debugfs, but direct callers must keep pattern in range. Mode programming trusts prior mode validation for bandwidth. HPD polling is timing sensitive and may suppress connector events if hardware state changes slowly.

Test signals: useful checks include DP hotplug, DPCD read, successful link training at all supported rates and lane downgrades, visible mode set at supported resolutions, interrupt enable/disable, debugfs colorbar patterns, and suspend/resume retaining a trainable link.
