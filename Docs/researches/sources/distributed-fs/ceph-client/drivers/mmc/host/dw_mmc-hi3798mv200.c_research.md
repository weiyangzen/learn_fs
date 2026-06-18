# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-hi3798mv200.c

Purpose: implements HiSilicon Hi3798MV200 DesignWare MMC glue, including devm-managed sample/drive clocks, SAP DLL tuning control, per-timing DT phase application, CIU clock-rate adjustment, and mixed-mode tuning.

Important APIs and functions: `dw_mci_hi3798mv200_init` gets enabled `ciu-sample` and `ciu-drive` clocks plus a syscon/regmap DLL control register. `dw_mci_hi3798mv200_set_ios` programs phase/HS400 registers, changes CIU rate, and applies phase-map values. `dw_mci_hi3798mv200_execute_tuning_mix_mode` temporarily enables tuning, scans phases, checks hardware edge-detect status, and stores the chosen sample phase into HS200/HS400/SDR104 phase maps.

Control flow: probe calls `dw_mci_pltfm_register` with `hi3798mv200_data`. Init resolves required clocks and `hisilicon,sap-dll-reg`. `set_ios` toggles `ENABLE_SHIFT` and `DDR_REG`, requests the MMC clock on `ciu_clk`, refreshes `host->bus_hz`, and applies `mmc_clk_phase_map` entries if present. Tuning clears DLL mode, scans 45-degree sample phases, treats either tuning-command failure or `SDMMC_TUNING_FIND_EDGE` as bad, disables tuning, selects a middle phase, updates phase maps, and clears interrupts.

State and persistence: private state holds the two clocks, CRG regmap, and DLL offset. Selected tuning phase is persisted in the in-memory phase map for later `set_ios`; hardware phase and DLL state are register/clock-provider state only.

Dependencies and integration points: depends on common DW MMC platform glue, Linux clocks, syscon/regmap, device-tree phase maps, and MMC tuning APIs.

Risks: missing DT phase entries only warn but may leave suboptimal timing. Tuning enable/disable failures abort the process. The selected tuned phase is copied to multiple high-speed timing modes regardless of which opcode/timing was tuned. Clock-rate changes can be rounded by the provider, so `host->bus_hz` must be trusted over requested `ios->clock`.

Test signals: DT probe with required clocks/syscon, phase-map parsing, HS200/HS400/SDR104 tuning, DLL mode bit transitions, clock rounding behavior, and shared DW transfer tests after runtime timing changes.
