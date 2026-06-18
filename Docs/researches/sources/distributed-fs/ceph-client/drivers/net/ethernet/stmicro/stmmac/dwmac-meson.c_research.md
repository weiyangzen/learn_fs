<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson.c

## Purpose
`dwmac-meson.c` is the older Amlogic Meson6/Meson8 stmmac glue layer. It programs a single auxiliary register bit to distinguish 10 Mbps from 100 Mbps operation.

## Important APIs, Types, and Functions
- `struct meson_dwmac` stores the device and a mapped control register.
- `meson6_dwmac_set_clk_tx_rate()` sets or clears `ETHMAC_SPEED_100` for SPEED_100 or SPEED_10.
- `meson6_dwmac_probe()` maps the second MMIO resource, installs the speed callback, and calls `stmmac_dvr_probe()`.

## Control Flow
Probe parses standard stmmac resources and DT config, allocates private data, maps resource index 1 for the Meson control register, assigns `bsp_priv` and `set_clk_tx_rate`, then lets stmmac register the netdev. Link-speed changes call back into the register update path.

## State and Persistence
The only persistent hardware state is the speed bit in the auxiliary Meson register. The driver does not track the current speed separately and does not allocate runtime resources beyond devm memory and MMIO mapping.

## Dependencies and Integration Points
It uses stmmac platform probing, MMIO read/write helpers, and ethtool speed constants. Compatible string: `amlogic,meson6-dwmac`.

## Risks and Edge Cases
- SPEED_1000 is ignored rather than rejected, matching the register's 10/100 role but relying on platform capability constraints elsewhere.
- The second MMIO resource must be present.
- There is no locking around the read-modify-write, so it assumes no other agent mutates the same register concurrently.

## Test Signals
Run 10 and 100 Mbps link tests and confirm `ETHMAC_SPEED_100` transitions. Probe should fail cleanly when the second resource is absent. Regression coverage should verify stmmac still handles unsupported gigabit modes outside this glue callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/dwmac-meson.c -->
