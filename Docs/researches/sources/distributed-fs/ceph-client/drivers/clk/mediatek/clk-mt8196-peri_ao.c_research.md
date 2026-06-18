# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-peri_ao.c

## sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8196-peri_ao.c

### Purpose
`clk-mt8196-peri_ao.c` implements the MT8196 always-on peripheral clock controller. It gates UART, PWM, SPI, flash interface, AP DMA, and MSDC1/MSDC2 clocks.

### Important APIs, Types, And Functions
The file defines three direct gate banks plus one HWV bank for SPI gates. `GATE_PERI_AO0`, `GATE_PERI_AO1`, `GATE_HWV_PERI_AO1`, and `GATE_PERI_AO2` fill `peri_ao_clks`, described by `peri_ao_mcd`. OF matching uses `mediatek,mt8196-pericfg-ao`, and probe/remove use `mtk_clk_simple_probe()`.

### Control Flow, State, And Persistence
The common simple probe registers the descriptor and publishes the provider. UART/PWM/flash/MSDC gates use direct set/clear operations; SPI clocks use HWV set/clear operations. State is hardware gate bits only.

### Dependencies, Integration Points, Risks, And Test Signals
Dependencies include top parents `uart`, `p_axi`, `pwm`, `spi*_b`, `sflash`, `msdc30_1`, and `msdc30_2`. Risks include early-console or storage clocks being gated unexpectedly, HWV SPI failures, and incorrect parent chains for flash/MSDC wrappers. Test signals include UART console, SPI transfer tests, PWM use, flash boot/storage access, MSDC probes, and clock debugfs.
