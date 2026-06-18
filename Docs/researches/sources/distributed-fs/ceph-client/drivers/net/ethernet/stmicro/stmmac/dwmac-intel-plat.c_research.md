# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-intel-plat.c

## Purpose
This is the Intel platform-bus DWMAC glue driver, currently matching Intel Keem Bay. It configures TX and PTP reference clock rates and hands control to the STMMAC core.

## Important APIs, Types, And Functions
- `struct intel_dwmac_data` stores desired PTP reference clock rate, TX clock rate, and whether TX clock management is required.
- `struct intel_dwmac` stores device, TX clock, and match data.
- `intel_eth_plat_probe()` gets STMMAC resources/DT config, allocates private state, enables and rates `tx_clk`, rates `clk_ptp_ref`, installs TX clock callbacks, and calls `stmmac_dvr_probe()`.
- `intel_eth_plat_remove()` removes STMMAC and disables the TX clock.
- `kmb_data` sets 200 MHz PTP ref and 125 MHz TX clock.

## Control Flow
Probe follows STMMAC platform setup, then applies Intel clock policy before invoking the core driver. On failure after enabling TX clock, it disables the clock. Remove unwinds core and clock state.

## State And Persistence
State is the devm-managed `intel_dwmac` and enabled clock rates. No extra runtime datapath state is managed here.

## Dependencies And Integration Points
Uses compatible `intel,keembay-dwmac`, clock framework, STMMAC platform helpers, and GMAC4 clock-rate callback `stmmac_set_clk_tx_rate`.

## Risks
- Assumes `plat_dat->clk_ptp_ref` is valid when clock-rate adjustment is requested.
- Clock rate mismatches are corrected at probe, which may fail if clocks are fixed or shared.
- Uses `stmmac_dvr_probe()` directly rather than `devm_stmmac_pltfr_probe()`, so remove must be correct.

## Test Signals
Probe Keem Bay DTs, verify `tx_clk` and PTP ref rates, traffic at multiple speeds, remove/unbind clock disable, and suspend/resume through STMMAC platform PM.
