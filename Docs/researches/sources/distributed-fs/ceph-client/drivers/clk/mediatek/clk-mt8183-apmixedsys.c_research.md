<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-apmixedsys.c -->
# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-apmixedsys.c

Purpose: This built-in driver registers MT8183 apmixedsys root PLLs plus 26 MHz gates for USB, APPLL, MIPI, modem, MMSYS, UFS, memory, and LVPLL-related consumers.

Important APIs, types, and functions: `apmixed_clks` uses `GATE_APMIXED` and one `CLK_IS_CRITICAL` APPLL 26M gate. `plls` defines ARM, CCI, main, universal, MFG, MSDC, TVD, MM, APLL1, and APLL2 PLLs with min/max, PCW, reset-bar, and divider-table data. `clk_mt8183_apmixed_probe` registers PLLs, gates, and an OF provider with rollback.

Control flow: As a `builtin_platform_driver`, it probes early for `mediatek,mt8183-apmixedsys`. It maps apmixedsys, allocates onecell data, registers PLLs, then low-frequency gates, and publishes the provider.

State and persistence behavior: PLL and gate state is volatile register state. Provider data is devm-allocated; no remove callback is used for normal unload. The critical gate is intended to remain enabled.

Dependencies and integration points: It depends on MT8183 bindings, `clk-pll.h`, `clk-gate.h`, and topckgen/main clock consumers that use PLL names and 26 MHz reference gates for USB, UFS, MIPI, display, modem, and audio.

Risks and edge cases: Root clock probe ordering is important. Incorrect PLL min/max/integer bit settings can break DVFS or rate changes. Critical gate flags must be preserved to avoid disabling required references.

Test signals: Early boot without clock-provider deferrals, PLL rates in clk summary, USB/UFS/MIPI/display/audio operation, critical gate enable state, and error-path rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8183-apmixedsys.c -->
