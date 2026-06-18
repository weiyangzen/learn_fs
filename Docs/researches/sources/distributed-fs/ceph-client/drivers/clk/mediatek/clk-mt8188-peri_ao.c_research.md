# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-peri_ao.c

## Purpose
`clk-mt8188-peri_ao.c` registers MT8188 always-on peripheral gates for Ethernet MAC/PHY, flash, and PCIe-related paths.

## Important APIs, Types, And Functions
The file defines `peri_ao_cg_regs`, `peri_ao_clks`, and `peri_ao_desc`, binding `mediatek,mt8188-pericfg-ao` through `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
Probe registers the gate table against the pericfg AO register block and publishes clocks for peripheral consumers. State persists only as common-clock-framework registrations and hardware gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers include Ethernet, flash, and PCIe controller nodes. Risks are incorrect gate bits or parent names that break device probe only when those peripherals are enabled in DT. Tests should include peripheral probe, link bring-up where applicable, unused-clock cleanup, and suspend/resume retention.
