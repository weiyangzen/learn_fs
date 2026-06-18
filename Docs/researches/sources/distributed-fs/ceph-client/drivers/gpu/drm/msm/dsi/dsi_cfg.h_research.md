# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_cfg.h

Purpose: This header defines MSM DSI hardware version constants, resource configuration structures, operation tables, and the configuration lookup API.

Important APIs and types: It declares major versions for v2 and 6G, many 6G minor version constants from v1.0 through v2.10, `DSI_6G_REG_SHIFT`, `VARIANTS_MAX`, `struct msm_dsi_config`, `struct msm_dsi_host_cfg_ops`, `struct msm_dsi_cfg_handler`, and `msm_dsi_cfg_get()`. The ops table abstracts hardware-generation differences in clock control, TX buffer management, DMA base retrieval, and clock-rate calculation.

Control flow and integration: `dsi_host.c` calls the lookup after reading hardware version registers, then uses the returned config for regulators, bus clocks, IO start/id matching, register offset shift, and host operation dispatch.

State and risks: No runtime state is owned. Risks are version constant mismatch and callback contract drift. Compile testing and hardware probe on each supported generation are the primary signals, with additional coverage for optional `clk_init_ver` and `tx_buf_put` callbacks.
