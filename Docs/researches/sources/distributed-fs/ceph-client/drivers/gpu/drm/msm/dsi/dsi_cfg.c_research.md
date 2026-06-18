# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_cfg.c

Purpose: This file maps DSI hardware versions to SoC-specific resource configuration and host operation tables. It is the compatibility matrix for regulators, bus clocks, register offset shifts, controller IO starts, and version-specific implementation callbacks.

Important APIs and data: Static `struct msm_dsi_config` entries cover APQ8064, MSM8974/APQ8084, MSM8916, MSM8976, MSM8994, MSM8996, MSM8998, SDM660, SDM845/QCM/SM variants, SC7280, SA8775P, SM8550, SM8650, and Kaanapali. Host ops select v2, 6G, 6G-v2, or 6G-v2.9 behavior for link clock setup/enable/disable, optional clock initialization, TX buffer allocation/access, DMA base lookup, and clock-rate calculation. `msm_dsi_cfg_get()` searches handlers from newest to oldest for an exact major/minor match.

Control flow: `dsi_host.c` reads hardware version registers, calls `msm_dsi_cfg_get()`, identifies controller id by matching the `dsi_ctrl` resource start against `io_start`, applies `io_offset`, gets regulators/clocks, and dispatches host behavior through the selected ops table.

State and dependencies: The file is static data with no runtime mutation. It depends on regulator bulk data types and host functions declared in `dsi.h`.

Risks and test signals: Risks include missing hardware version entries, wrong regulator loads, bus clock names, IO starts, or ops selection. A wrong `io_offset` shifts every register access. Test signals include probe across supported SoCs, regulator/clock acquisition, id detection for DSI0/DSI1, v2 versus 6G TX buffer behavior, OPP rate votes, and v2.9 clock reparenting.
