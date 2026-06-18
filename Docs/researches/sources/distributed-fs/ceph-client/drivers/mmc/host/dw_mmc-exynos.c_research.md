# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-exynos.c

Purpose: implements Samsung Exynos and Axis ARTPEC-8 extensions for the shared DesignWare MMC core, covering SoC type detection, clock-divider/timing programming, SMU security setup, HS400 strobe control, tuning, extended timeout support, and Exynos-specific PM sequencing.

Important APIs and functions: main hooks in `exynos_drv_data` and `artpec_drv_data` include `dw_mci_exynos_priv_init`, `dw_mci_exynos_set_ios`, `dw_mci_exynos_parse_dt`, `dw_mci_exynos_execute_tuning`, `dw_mci_exynos_prepare_hs400_tuning`, and ARTPEC timeout helpers. Runtime/system PM wrappers include `dw_mci_exynos_runtime_resume`, `dw_mci_exynos_suspend_noirq`, and `dw_mci_exynos_resume_noirq`.

Control flow: probe enables runtime PM, selects drv_data from compatible strings, and registers through `dw_mci_pltfm_register`. DT parsing allocates private data, identifies controller type, reads fixed or DT CIU divider and timing arrays, and stores optional HS400 DQS delay. Init configures SMU windows for non-encrypted access on SMU variants, saves/restores HS400 strobe registers, enables quirks, and adjusts `bus_hz` by the CIU divider. `set_ios` selects SDR/DDR/HS400 timing registers, may double requested clock for DDR/HS400, configures DQS, and retunes the CIU clock. Tuning cycles sample phases, records successful candidates, chooses the best window, and saves the tuned sample for HS400.

State and persistence: `struct dw_mci_exynos_priv_data` stores controller type, divider, SDR/DDR/HS400 timing words, tuned sample, current speed, DQS delay, and saved HS400 registers. Register state is restored on runtime resume and adjusted on each `set_ios`; no disk persistence exists.

Dependencies and integration points: depends on `dw_mmc.h`, `dw_mmc-pltfm.h`, `dw_mmc-exynos.h`, OF matching, clocks, runtime PM, and MMC tuning APIs. It uses the shared DW core for request/DMA/PIO/interrupt handling and only overrides variant behavior through `dw_mci_drv_data`.

Risks: DT timing arrays are mandatory for Exynos paths; missing values fail parse. Clock and divider math must match SoC register layouts, with separate `CLKSEL` versus `CLKSEL64` paths. HS400 is unavailable on older types and ARTPEC-8. Resume must clear stale wakeup interrupt bits or IRQ storms can occur. ARTPEC extended timeout uses a different TMOUT encoding, so the matching get/set hooks must be paired.

Test signals: DT probe for each compatible, SDR/DDR/HS200/HS400 mode transitions, tuning candidate selection, SMU register setup, runtime suspend/resume, noirq resume wakeup-bit clearing, ARTPEC long timeout behavior, and shared DW transfer/error tests.
