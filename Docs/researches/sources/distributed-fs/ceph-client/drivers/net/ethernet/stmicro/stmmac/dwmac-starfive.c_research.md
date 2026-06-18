<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-starfive.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-starfive.c

## Purpose
`dwmac-starfive.c` is the StarFive JH7100/JH7110 DWMAC platform glue layer. It enables TX/GTX clocks, selects RGMII or RMII mode through a syscon phandle, optionally programs a JH7100 GTX clock delay chain, and configures stmmac DMA/cache and low-power flags.

## Important APIs, Types, and Functions
- `struct starfive_dwmac_data` stores optional GTX delay-chain value.
- `struct starfive_dwmac` stores device and match data.
- `starfive_dwmac_set_mode()` maps stmmac PHY mode to syscon field bits and writes optional `JH7100_SYSMAIN_REGISTER49_DLYCHAIN`.
- `starfive_dwmac_probe()` gets resources, parses stmmac DT, enables `tx` and `gtx` clocks, selects TX clock-rate callback policy, sets flags, and probes stmmac.

## Control Flow
Probe prepares stmmac data, allocates private state, enables required clocks, conditionally installs `stmmac_set_clk_tx_rate` unless `starfive,tx-use-rgmii-clk` says the external RGMII clock is used, sets low-power and DMA cache flags, programs syscon mode/delay, and calls `stmmac_dvr_probe()`.

## State and Persistence
Private state is devm-managed. Hardware state includes syscon interface selection, optional JH7100 delay-chain register, enabled clocks, and stmmac DMA/cache settings.

## Dependencies and Integration Points
It depends on syscon/regmap phandle arguments, clk APIs, stmmac platform helpers, and device properties. Compatible strings are `starfive,jh7100-dwmac` and `starfive,jh7110-dwmac`.

## Risks and Edge Cases
- Only RGMII and RMII selector values are accepted.
- `starfive,syscon` must provide offset and shift arguments.
- TX clock rate programming depends on the board-level `starfive,tx-use-rgmii-clk` property.
- JH7100 delay-chain programming is unconditional for that match data.

## Test Signals
Test JH7100 and JH7110 DTs, RGMII/RMII mode selection, external-vs-internal TX clock property behavior, GTX delay-chain write on JH7100, and traffic after speed transitions with and without `set_clk_tx_rate`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-starfive.c -->
