# sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/mediatek.c

Purpose: Generic MediaTek ARMv7 DT machine descriptor with early clock/timer initialization.

Important APIs/types/functions: Defines `mediatek_timer_init()`, the `mediatek_board_dt_compat[]` root-compatible list, and `DT_MACHINE_START(MEDIATEK_DT, ...)`.

Control flow: During `.init_time`, selected MT6589/MT7623/MT8135/MT8127 systems map the GPT6 control register at physical `0x10008060`, write `0x31` to enable/free-run GPT6 so the architectural timer clock is ungated, unmap it, then call `of_clk_init(NULL)` and `timer_probe()`. Machine selection matches MT2701, MT6572, MT6582, MT6589, MT6592, MT7623, MT7629, MT8127, or MT8135 root compatibles.

State and persistence: No persistent software state. Hardware state is limited to GPT6 clock/free-run enable on the older listed SoCs; clocksource state is registered by generic timer/clock drivers.

Dependencies and integration points: Depends on OF machine matching, fixed GPT6 physical register knowledge for older SoCs, common clock init, and clocksource timer probing.

Risks: `ioremap()` of GPT6 is not checked before `writel()`, so a mapping failure would crash during early boot. The hard-coded physical address and magic value are SoC-specific and bypass DT resources. SoCs not in the conditional rely entirely on normal DT timer/clock nodes.

Test signals: Boot each compatible family, confirm arch timer availability, and regression-test MT6589/MT7623/MT8135/MT8127 where GPT6 must be explicitly ungated.
