# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-phy-v1.c

## Purpose
`xgbe-phy-v1.c` implements the PHY backend for first-generation platform devices. It supports backplane-style KR at 10G and either KX at 1G or KX at 2.5G depending on the `amd,speed-set` property. It directly programs PCS and SerDes registers using platform-provided SerDes resources.

## Important APIs, Types, And Functions
- `struct xgbe_phy_data` stores the speed set and per-speed SerDes tuning arrays.
- Property names such as `amd,serdes-blwc`, `amd,serdes-cdr-rate`, `amd,serdes-pq-skew`, `amd,serdes-tx-amp`, `amd,serdes-dfe-tap-config`, and `amd,serdes-dfe-tap-enable` override default tuning.
- `xgbe_phy_kr_mode`, `xgbe_phy_kx_2500_mode`, and `xgbe_phy_kx_1000_mode` program PCS and SerDes speed-specific registers.
- `xgbe_phy_start_ratechange`/`xgbe_phy_complete_ratechange` coordinate SerDes rate changes and RX reset.
- `xgbe_phy_an_outcome` resolves CL73 AN result and pause/FEC/link-partner advertisement.
- `xgbe_phy_use_mode`, `xgbe_phy_get_mode`, `xgbe_phy_switch_mode`, and `xgbe_phy_valid_speed` expose mode policy to the common MDIO layer.
- `xgbe_phy_reset` performs PCS software reset with timeout.
- `xgbe_init_function_ptrs_phy_v1` fills the implementation callback table.

## Control Flow
Init allocates PHY data, reads `amd,speed-set`, loads optional SerDes arrays or defaults, builds supported link modes, and records `pdata->phy_data`. The common MDIO layer then chooses modes and starts CL73 negotiation. Mode changes set PCS type/speed, power-cycle PCS, assert SerDes ratechange, write speed/tuning fields, release ratechange, wait for RX/TX ready, and reset RX DFE. AN outcome reads local and partner advertisement registers to choose KR or KX and resolve pause.

## State And Persistence
Persistent-for-device runtime state is the allocated `struct xgbe_phy_data`, including speed-set and tuning arrays. Link advertisement state is stored in `pdata->phy.lks`; current mode is inferred from PCS `MDIO_CTRL2` rather than cached. There is no external PHY or SFP state in v1.

## Dependencies And Integration Points
This backend is selected by platform version data in `xgbe-platform.c`. It depends on platform resources for `rxtx_regs`, `sir0_regs`, and `sir1_regs`, MDIO register access through common macros, and the common AN/link state machine in `xgbe-mdio.c`.

## Risks
SerDes tuning properties must have exactly `XGBE_SPEEDS` entries and valid board-specific values; bad firmware properties can prevent link. Ratechange waits only a bounded count and logs debug on not-ready status before continuing to RX reset. v1 supports only full duplex and a limited speed set; ethtool fixed-speed validation must reject unsupported values. PCS reset timeout returns `-ETIMEDOUT`.

## Test Signals
Test both `XGBE_SPEEDSET_1000_10000` and `XGBE_SPEEDSET_2500_10000`, default and firmware-provided SerDes tuning, CL73 KR/KX negotiation, fixed-speed configuration, PCS reset timeout handling, and link flap recovery. `ethtool` supported/advertised modes should match the speed-set property.
