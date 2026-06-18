# sources/distributed-fs/ceph-client/drivers/mmc/host/dw_mmc-rockchip.c

Purpose: implements Rockchip-specific DesignWare MMC support for RK2928, RK3288, and RK3576 variants, including clock scaling, external or internal phase programming, tuning-window selection, SDIO IRQ bit setup, and runtime PM phase restore.

Important APIs and functions: hooks include `dw_mci_rk3288_set_ios`, `dw_mci_rk3288_execute_tuning`, `dw_mci_rk3288_parse_dt`, `dw_mci_rk3576_parse_dt`, and `dw_mci_rockchip_init`. Phase helpers include `rockchip_mmc_get_phase`, `rockchip_mmc_set_phase`, and internal delay conversion helpers. Runtime PM wrappers save and restore internal phase registers.

Control flow: probe requires OF, enables runtime PM/autosuspend, selects drv_data, and registers through platform glue. Common DT parsing reads desired number of tuning phases and default sample phase. RK3288 uses `ciu-drive` and `ciu-sample` clocks; RK3576 uses internal phase registers. `set_ios` sets CIU clock to `ios->clock * 2` with DDR52 8-bit adjustment, updates `host->bus_hz`, applies sample phase from DT/default/tuned phase, and sets drive phase by timing mode. Tuning scans configured phases, skips ahead after bad samples, merges wraparound ranges, selects the middle of the longest valid range, and programs it.

State and persistence: `struct dw_mci_rockchip_priv_data` stores clock handles, default sample phase, phase count, internal-phase mode, and saved sample/drive phases for runtime suspend. Register or clock-provider phase state is re-applied after runtime resume.

Dependencies and integration points: depends on shared DW platform/core code, Linux clocks, OF, MMC slot GPIO, runtime PM, and hardware bitfield helpers. It uses common caps for CMD23 on RK3288/RK3576 and the shared request/DMA/PIO engine.

Risks: phase math for internal delays assumes roughly 60 ps delay elements and can be off by hardware variation. Tuning quality depends on `rockchip,desired-num-phases`; too few phases can miss narrow valid windows, too many can slow tuning. Missing sample clock makes tuning fail on external-phase variants. Runtime PM must restore internal phase registers or tuned timing is lost.

Test signals: DT probe for RK2928/RK3288/RK3576, clock-rate and phase inspection, tuning logs and selected phase, SDIO IRQ behavior using bit 8, runtime autosuspend/resume with retained tuning, DDR52/HS200/SDR104 transfers, and error-path tuning tests.
