<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-renesas-gbeth.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-renesas-gbeth.c

## Purpose
`dwmac-renesas-gbeth.c` is the Renesas GBETH/GMAC glue layer for RZ/V and RZ/G class SoCs. It supplies variant clock lists, optional reset ownership, TX clock rate callback, hardware timestamp flags, optional MIIC PCS creation, and stmmac init/exit hooks.

## Important APIs, Types, and Functions
- `struct renesas_gbeth_of_data` defines clock names, stmmac flags, reset handling, TX clock policy, and PCS presence.
- `struct renesas_gbeth` stores match data, platform data, reset control, and device pointer.
- `renesas_gmac_pcs_init/exit/select_pcs()` create and expose a MIIC phylink PCS from `pcs-handle`.
- `renesas_gbeth_init()` deasserts reset and enables bulk clocks.
- `renesas_gbeth_exit()` disables clocks and reasserts reset.
- `renesas_gbeth_probe()` allocates state, obtains clocks/reset, configures stmmac callbacks, and probes stmmac.

## Control Flow
Probe parses stmmac resources and DT data, allocates `renesas_gbeth`, builds the bulk clock array from match data, obtains the TX clock, optionally gets an exclusive reset, fills `bsp_priv`, optional `set_clk_tx_rate`, init/exit, low-power/TX LPI and timestamp flags, and optional PCS hooks. `devm_stmmac_pltfr_probe()` then invokes the stmmac lifecycle. Init deasserts reset before enabling clocks and asserts reset if clock enable fails.

## State and Persistence
State is devm-managed per device. Hardware state includes clock enable counts, reset line state, stmmac MAC registers, and optional MIIC PCS object lifetime. There is no persistent file-backed state.

## Dependencies and Integration Points
It depends on clk bulk APIs, reset controls, MIIC PCS helpers, OF phandles, and stmmac platform helpers. Compatible strings are `renesas,r9a08g046-gbeth`, `renesas,r9a09g077-gbeth`, and `renesas,rzv2h-gbeth`.

## Risks and Edge Cases
- Variant clock names differ: GBETH expects `tx`, `tx-180`, `rx`, `rx-180`; GMAC expects only `tx`.
- Reset handling is variant-specific; using the wrong compatible can leave reset ownership mismatched.
- Missing `tx` clock fails probe even when other clocks exist.
- PCS creation is optional and depends on `pcs-handle`.

## Test Signals
Run probe/remove and suspend/resume on each compatible, validate reset and clock sequencing, check TX clock rate changes where enabled, verify MIIC PCS attach/detach with SGMII-like links, and confirm hardware timestamp latency flags do not regress PTP tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-renesas-gbeth.c -->
