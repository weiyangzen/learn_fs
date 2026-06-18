# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt8195-infra_ao.c

## Purpose
`clk-mt8195-infra_ao.c` implements the MT8195 always-on infrastructure clock provider. It covers bus, security, DMA, UART/SPI/I2C, thermal, PMIC, debug, and other infra clocks that support early and low-power operation.

## Important APIs, Types, And Functions
The file defines five infra AO gate banks, a large `infra_ao_clks` table with multiple `CLK_IS_CRITICAL` entries, and `infra_ao_desc` for `mediatek,mt8195-infracfg_ao`. It includes MT8195 reset bindings but does not attach a reset descriptor in the visible descriptor.

## Control Flow, State, And Persistence
`mtk_clk_simple_probe()` registers all infra AO gates and publishes an OF provider. Critical clocks are protected from automatic disable. State persists as hardware gate state and CCF registration until simple remove.

## Dependencies, Integration Points, Risks, And Test Signals
Dependencies include MT8195 infra clock IDs and many SoC peripheral consumers. Risks are system-wide: a wrong critical flag, parent, or gate bit can break boot, interrupt/security paths, serial console, or PMIC access. Test signals include boot with unused-clock cleanup, serial/I2C/SPI/PWM/thermal probe, suspend/resume, and `clk_summary` critical gate status.
