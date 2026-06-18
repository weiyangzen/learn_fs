# sources/distributed-fs/ceph-client/drivers/clk/mvebu/ap806-system-controller.c

Purpose: AP806/AP807 system-controller clock provider for fixed root and derived AP clocks based on Sample At Reset frequency mode.

Important APIs/functions: `ap806_syscon_common_probe` reads the SAR register and registers six clocks. `ap806_get_sar_clocks` and `ap807_get_sar_clocks` decode frequency modes. Both legacy syscon and child clock platform drivers call the common probe.

Control flow: probe obtains the syscon regmap from either the node itself or its parent, decodes CPU and DDR clock MHz, registers fixed-rate cluster PLLs, a fixed 1.2 GHz clock, MSS and SDIO fixed-factor clocks, AP-DCLK, then publishes a onecell provider.

State and persistence: clocks are fixed after boot from SAR state. A static `ap806_clks` array backs the provider.

Dependencies and integration: CCF, regmap syscon, AP/CP unique names, platform drivers for legacy `marvell,ap806-system-controller` and modern `marvell,ap806-clock`/`ap807-clock`.

Risks: static clock storage means multiple instances would conflict. Error unwind labels unregister `ap806_clks[5]` with fixed-factor API even though AP-DCLK is fixed-rate. Unsupported SAR modes abort all provider registration.

Test signals: AP806/AP807 SAR mode matrix, legacy binding warnings, onecell clock indexes, and boot clock rate validation.
