# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-peri_ao.c

## Purpose
`clk-mt8195-peri_ao.c` registers MT8195 always-on peripheral clocks for Ethernet, flash/NFI/ECC, and PCIe-related functions.

## Important APIs, Types, And Functions
The driver defines `peri_ao_cg_regs`, `peri_ao_clks`, `peri_ao_desc`, and OF compatible `mediatek,mt8195-pericfg_ao`, using `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()`.

## Control Flow, State, And Persistence
Probe registers the peripheral AO gate table and exposes the clocks to OF consumers. State is limited to CCF registration and hardware gate bits.

## Dependencies, Integration Points, Risks, And Test Signals
Consumers include Ethernet, flash, NAND/ECC, and PCIe devices. Risks include rarely tested peripheral gates drifting from DT bindings. Test signals include enabled peripheral probe, link/storage tests, unused-clock cleanup, and suspend/resume.
