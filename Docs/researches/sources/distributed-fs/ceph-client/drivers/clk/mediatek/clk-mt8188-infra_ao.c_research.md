# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8188-infra_ao.c

## Purpose
`clk-mt8188-infra_ao.c` implements the MT8188 always-on infrastructure clock provider. It exposes a large set of infra gates for security, DMA, UART, SPI, PWM, I2C, thermal, debug, and bus fabric functions that must often remain available early or during low-power transitions.

## Important APIs, Types, And Functions
The driver defines five `mtk_gate_regs` banks, an `infra_ao_clks` array with critical flags on essential clocks, `infra_ao_rst_desc` for reset-controller integration, and `infra_ao_desc`. It matches `mediatek,mt8188-infracfg-ao` and uses `mtk_clk_simple_probe()`/`remove()`.

## Control Flow, State, And Persistence
The simple probe registers gate clocks from all infra AO banks and the reset controller described by `infra_ao_rst_desc`. `CLK_IS_CRITICAL` entries are retained by the CCF and should not be disabled by unused-clock cleanup. State persists in hardware gate bits and reset-controller registration until remove.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include `mt8188-resets.h`, infra clock IDs, and many peripheral consumers. Risks are high because disabling a critical infra clock can break interrupt, security, bus, or debug access; reset-map mismatches can reset the wrong block. Test signals include boot with unused-clock cleanup, peripheral probe across UART/SPI/I2C/PWM, reset-controller consumers, suspend/resume, and `clk_summary` showing critical infra clocks protected.
