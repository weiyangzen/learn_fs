# sources/distributed-fs/ceph-client/drivers/ufs/host/ti-j721e-ufs.c

## Purpose
Implements the TI J721E UFS subsystem glue layer that prepares a Cadence UFS controller child. It programs subsystem control bits for MPHY reference clock frequency and PCS reset, then populates child platform devices.

## Important APIs, types, and functions
`struct ti_j721e_ufs` stores the mapped subsystem register base and the control register value to restore on resume. `ti_j721e_ufs_probe()` uses `devm_platform_ioremap_resource()`, runtime PM, `devm_clk_get()`, `clk_get_rate()`, `writel()`, and `of_platform_populate()`. `ti_j721e_ufs_resume()` rewrites the cached control value. Remove depopulates children and disables runtime PM.

## Control flow and state
Probe allocates private state, maps registers, resumes the device, detects a 26 MHz MPHY clock, sets `TI_UFS_SS_CLK_26MHZ` when needed, deasserts PCS reset via `TI_UFS_SS_RST_N_PCS`, stores drvdata, and creates child devices. Persistent state is the cached `reg` field used for sleep resume.

## Dependencies and integration points
Depends on OF platform population, runtime PM, clock framework, and a downstream child node that normally binds the Cadence UFS controller. The Kconfig description makes this a glue layer, not the UFSHCD host itself.

## Risks and test signals
Risks include incorrect refclk detection for non-26 MHz inputs, child population failure after PM enable, and lost subsystem register state across suspend. Test signals are child Cadence probe success, correct `TI_UFS_SS_CTRL` value before and after resume, and balanced runtime PM on probe failure and remove.
