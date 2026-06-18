# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-starfive.c

Purpose: supplies StarFive JH7110-specific DesignWare MMC hooks for DDR clock-rate handling and sample delay-chain tuning.

Important APIs and functions: `dw_mci_starfive_set_ios` adjusts CIU clocking for DDR52/DDR50 modes. `dw_mci_starfive_set_sample_phase` writes the sample phase field in `UHS_REG_EXT`. `dw_mci_starfive_execute_tuning` scans 32 delay-chain positions and selects the midpoint of the first valid range. Probe registers shared DW platform glue with `starfive_data`.

Control flow: matching `starfive,jh7110-mmc` selects `starfive_data`. For DDR timing, `set_ios` requests 100 MHz when the desired clock is around 50-52 MHz, otherwise it leaves the shared core to use internal dividers. Tuning writes each sample phase, clears interrupts, sends the tuning command, records the first pass and first subsequent fail as a valid window, then programs the midpoint or returns `-EINVAL` if no phase worked.

State and persistence: no private allocation is used. Sample phase and clock rate are held in controller/clock-provider state for the active device lifetime.

Dependencies and integration points: depends on `dw_mmc.h`, `dw_mmc-pltfm.h`, Linux clock APIs, OF platform matching, and MMC tuning helpers. It relies entirely on the shared DW core for requests, interrupts, DMA/PIO, and PM is not customized.

Risks: the tuning algorithm only uses the first contiguous valid range and does not handle wraparound or multiple windows as thoroughly as Rockchip/Exynos code. `mdelay(1)` in phase setting is a busy wait. DDR clock fallback logs debug if external divider use is needed, so misclocking may be quiet unless debugging is enabled.

Test signals: JH7110 DT probe, DDR52/DDR50 clock-rate checks, tuning success/failure across cards, sample phase register inspection, and shared DW data-transfer stress.
