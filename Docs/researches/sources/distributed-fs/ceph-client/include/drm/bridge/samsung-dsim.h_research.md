# sources/distributed-fs/ceph-client/include/drm/bridge/samsung-dsim.h

Purpose: shared interface and state definition for Samsung DSIM MIPI DSI host/bridge support across Exynos and i.MX variants.

Important APIs/types/functions: `DSIM_STATE_*`, `enum samsung_dsim_type`, `samsung_dsim_hw_is_exynos`, `struct samsung_dsim_transfer`, `struct samsung_dsim_driver_data`, `struct samsung_dsim_host_ops`, `struct samsung_dsim_plat_data`, `struct samsung_dsim`, `samsung_dsim_probe`, `samsung_dsim_remove`, and `samsung_dsim_pm_ops`.

Control flow: platform drivers select hardware/platform data; probe maps registers/resources and initializes host/bridge state. MIPI transfers are queued on `transfer_list`, completed by IRQ/TE paths, and bridge state tracks enable, initialization, command low-power mode, and video-output availability.

State and persistence: `struct samsung_dsim` stores runtime mode, MMIO, PHY, clocks, supplies, IRQs, TE GPIO, PLL/HS/escape rates, lanes, format, swap flags, state bits, brightness property, completions, transfer list, locks, and private data. Hardware state is restored through PM.

Dependencies and integration points: GPIO, regulators, clocks, PHY, DRM bridge/atomic/MIPI DSI/OF helpers, platform devices, panels, and SoC data tables.

Risks and test signals: variant register quirks, PLL bounds, supply/clock ordering, transfer races, and Exynos/i.MX differences are risks. Test probe/remove, PM, command/video panels, TE IRQ, transfer timeout, PLL rates, lane swaps, and all hardware types.
