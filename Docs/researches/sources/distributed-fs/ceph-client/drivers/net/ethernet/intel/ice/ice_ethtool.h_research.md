# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_ethtool.h

## Purpose

`ice_ethtool.h` provides local ethtool support definitions for the ICE driver. It is not a broad public API header; it primarily defines helper data structures and lookup tables used by `ice_ethtool.c` to translate ICE hardware PHY type bits into Linux ethtool link mode bits and to format extended register/SerDes equalization dump data.

## Important APIs, Types, and Data

`struct ice_phy_type_to_ethtool` maps an ICE admin queue link speed bitmask (`aq_link_speed`) to an ethtool link mode bit (`link_mode`). The `ICE_PHY_TYPE()` macro builds entries from ICE admin queue speed names and ethtool mode names.

`phy_type_low_lkup[]` and `phy_type_high_lkup[]` are static const lookup tables indexed by ICE PHY type bit positions. The low table covers PHY type low bits from 100M through 100G variants. The high table covers newer 100G and 200G variants. `ice_ethtool.c` iterates these arrays in `ice_phy_type_to_ethtool()` and sets supported/advertised bits when the corresponding PHY type masks are present.

`struct ice_serdes_equalization_to_ethtool` is a packed driver-side presentation structure for many SerDes equalization parameters. It contains RX equalization values such as pre/post taps, CTLE gain/bandwidth, and DFE values, plus TX equalization values such as pre, post, and attenuation. `struct ice_regdump_to_ethtool` groups up to four of these per port because a multilane port can have up to four SerDes lanes.

`struct ice_port_topology` holds the derived physical topology for a logical port: PCS port, primary SerDes lane, SerDes lane count, and PCS quad select. It is filled in `ice_get_port_topology()` and then used for extended register dump and FEC counter lookup.

## Control Flow and Integration

The header's PHY lookup tables are consumed at runtime by the ethtool link settings path. `ice_phy_type_to_ethtool()` receives PHY type low/high masks from current media, NVM, or link override state. It then walks `phy_type_low_lkup[]` and `phy_type_high_lkup[]`, setting ethtool supported and advertising bits according to the tables.

The equalization and topology structures are used in the register dump path. `ice_get_regs_len()` includes `sizeof(struct ice_regdump_to_ethtool)`, `ice_get_extended_regs()` derives `struct ice_port_topology`, and `ice_get_tx_rx_equa()` fills each `struct ice_serdes_equalization_to_ethtool` entry with values returned by firmware admin queue calls.

## State and Persistence Behavior

This header itself owns no mutable runtime state. Its lookup arrays are static const data compiled into the driver. The data they help populate is transient ethtool output or driver stack/local structures. The only persistence concern is ABI-like: changing the layout of `struct ice_regdump_to_ethtool` changes what `ice_get_regs()` copies into the ethtool register dump buffer, and changing link mode table entries changes userspace-visible supported/advertised link modes.

## Dependencies and Integration Points

The header assumes ICE admin queue speed macros such as `ICE_AQ_LINK_SPEED_*`, PHY type bit ordering from ICE admin queue headers, and Linux ethtool link mode bit names. It is included by `ice_ethtool.c` and is tightly coupled to the ICE firmware's definition of PHY type low/high bit positions.

## Risks and Edge Cases

The highest risk is incorrect table indexing. Each array index must correspond to the hardware PHY type bit documented in ICE admin queue headers. A shifted or stale entry would advertise the wrong cable/media capability to userspace and could allow invalid speed selections. The high table also only defines currently supported high bits; future PHY types require explicit additions.

The register dump structs are used as raw ethtool data. Field layout changes should be treated cautiously because userspace tooling may decode this binary region by driver version.

## Test Signals

Test through `ethtool <dev>` and `ethtool --show-fec`/link settings on ports with varied media: SFP, QSFP, BASE-T, backplane, direct attach, 25G/50G/100G/200G capable modules, link up and link down. Register dump tests should verify `ethtool -d` length and decode stability, especially on one-lane, two-lane, and four-lane ports.
