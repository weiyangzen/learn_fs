# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/phy_lcn.h

## Purpose

`phy_lcn.h` defines the small LCN-PHY register/state interface used by `phy_lcn.c`. It names the LCN AFE/RF/table access registers, declares the per-device LCN state structure, and exports the `b43_phyops_lcn` operation table.

The header is intentionally compact compared with G/HT/LP headers. Most LCN register use in `phy_lcn.c` is still raw numeric offsets; this header only names the common AFE, RF control, and table port registers.

## Important APIs, Types, and Macros

- `B43_PHY_LCN_AFE_CTL1` and `B43_PHY_LCN_AFE_CTL2` are AFE control registers used for analog power toggling and AFE set/unset sequencing.
- `B43_PHY_LCN_RF_CTL1` through `B43_PHY_LCN_RF_CTL7` name RF control registers manipulated by software RF kill.
- `B43_PHY_LCN_TABLE_ADDR`, `B43_PHY_LCN_TABLE_DATALO`, and `B43_PHY_LCN_TABLE_DATAHI` define the LCN table access ports used for TX power offset clearing and table operations.
- `struct b43_phy_lcn` stores LCN runtime power-control state: `hw_pwr_ctl`, `hw_pwr_ctl_capable`, and `tx_pwr_curr_idx`.
- `extern const struct b43_phy_operations b43_phyops_lcn` exports the operation table implemented in `phy_lcn.c`.

## Control Flow and Integration

Common b43 PHY dispatch selects `b43_phyops_lcn` for LCN PHY devices. The operation callbacks allocate and prepare `struct b43_phy_lcn`, then `phy_lcn.c` uses the register constants in this header during initialization, channel switching, RF kill, analog switching, table clearing, and radio/PHY access.

The table access constants are used directly by routines that stream zeros into LCN TX power offset tables. The RF control constants are used by RF kill to set and clear power-down override bits. The AFE control constants are used by both analog switching and the AFE power-cycle helper.

## State and Persistence

The LCN state structure is volatile and per-device. It is allocated during PHY allocation, zeroed in `prepare_structs()`, and freed on PHY teardown. Its fields are a software mirror/control surface for TX power behavior; current code mostly uses them to choose the fixed software TX gain path and to remember the current TX power index during sense setup.

No on-disk persistence exists. Hardware state persists only in the programmed PHY/radio registers until reset, channel switch, RF kill, or another init path changes it.

## Dependencies

The header includes `phy_common.h` for common b43 PHY types and register encodings. It relies on `B43_PHY_OFDM()` for register address construction and forward-declares `struct b43_phy_operations`. It is consumed by `phy_lcn.c`, `tables_phy_lcn.c`, and common PHY selection code.

## Risks and Edge Cases

- The header names only a subset of LCN registers; most raw offsets still live in `phy_lcn.c`, which makes audits and refactors harder.
- `hw_pwr_ctl_capable` exists, but the implementation logs that hardware TX power control is unsupported when it is set. Consumers should not assume this field means the path works.
- `tx_pwr_curr_idx` has no explicit nonzero initializer in the header or prepare path; code that restores the TX power index must tolerate the default zero.
- RF kill relies on the exact RF control bit masks in `phy_lcn.c`; changing these constants requires hardware validation.

## Test Signals

Compile tests should include LCN support and table code. Runtime checks should verify `dev->phy.lcn` is allocated, zeroed, and freed correctly; AFE control writes hit the expected registers; RF kill changes only the intended RF control registers; and LCN table clearing writes through the named table address/data ports.
