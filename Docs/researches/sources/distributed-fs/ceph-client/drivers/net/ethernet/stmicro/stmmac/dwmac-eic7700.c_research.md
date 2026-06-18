# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-eic7700.c

## Purpose
This is the Eswin EIC7700 DWMAC QoS glue driver. It programs Eswin HSP syscon registers for interface selection, low-power AXI behavior, and TX/RX delay, configures clocks, and delegates the Ethernet core to STMMAC.

## Important APIs, Types, And Functions
- `struct eic7700_qos_priv` stores the STMMAC platform data for clock callbacks.
- `eic7700_clks_config()` prepares/enables or disables the bulk clock list.
- `eic7700_dwmac_init()`/`exit()` wrap clock enable/disable for STMMAC platform callbacks.
- `eic7700_dwmac_suspend()`/`resume()` delegate to runtime PM force suspend/resume.
- `eic7700_dwmac_probe()` reads required delay properties, looks up the HSP syscon regmap, reads offsets from the same phandle property, writes interface and delay registers, obtains optional clocks, installs callbacks, and probes STMMAC.

## Control Flow
Probe gets resources and standard STMMAC DT config, requires `rx-internal-delay-ps` and `tx-internal-delay-ps`, converts each to 0.1 ns units capped at `0x7f`, programs HSP control offsets, creates a three-clock bulk list (`tx`, `axi`, `cfg`), attaches `clks_config`, init/exit/suspend/resume callbacks, and calls `devm_stmmac_pltfr_probe()`.

## State And Persistence
State is devm-managed `eic7700_qos_priv`, STMMAC platform data, and syscon hardware registers. Runtime clock state follows STMMAC init/exit and PM callbacks.

## Dependencies And Integration Points
Depends on OF, syscon/regmap, runtime PM, clocks, STMMAC platform helpers, and compatible `eswin,eic7700-qos-eth`.

## Risks
- Delay properties are mandatory; missing either fails probe.
- The `eswin,hsp-sp-csr` phandle is used both as a regmap reference and as a container for three offset cells; DT binding must match exactly.
- Clock callbacks rely on `plat_dat->clks` and `num_clks` being stable.
- Register writes are not read back or masked for all fields, so integration depends on correct offsets and reset state.

## Test Signals
Probe with valid/missing delay properties, verify syscon writes, test all clocks optional/present, open/close PM cycles, suspend/resume, link speed changes, and STMMAC traffic.
