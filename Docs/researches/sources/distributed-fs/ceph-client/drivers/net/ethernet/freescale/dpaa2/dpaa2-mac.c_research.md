# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/dpaa2/dpaa2-mac.c

## Purpose
`dpaa2-mac.c` is the DPAA2 DPMAC support library used by DPNI Ethernet and switch ports. It opens DPMAC MC objects, discovers firmware/node/PHY interface details, creates phylink and optional Lynx PCS/SerDes integration, propagates phylink state into DPMAC link state, and fetches DPMAC hardware statistics for ethtool.

## Important APIs and functions
Public exports include `dpaa2_mac_open()`, `dpaa2_mac_close()`, `dpaa2_mac_connect()`, `dpaa2_mac_disconnect()`, `dpaa2_mac_start()`, `dpaa2_mac_stop()`, `dpaa2_mac_get_strings()`, `dpaa2_mac_get_ethtool_stats()`, and standardized RMON/pause/control/MAC stat getters. Feature detection is handled by `dpaa2_mac_detect_features()` based on DPMAC API versions for protocol change, bundled stats, and standard stats. `dpaa2_mac_get_node()` maps DPMAC IDs to OF or ACPI firmware nodes. `phy_mode()` and `dpmac_eth_if_mode()` translate DPMAC protocol enums to Linux `phy_interface_t` and back.

Phylink callbacks are `dpaa2_mac_select_pcs()`, `dpaa2_mac_config()`, `dpaa2_mac_link_up()`, and `dpaa2_mac_link_down()`. PCS and SerDes helpers include `dpaa2_pcs_create()`, `dpaa2_pcs_destroy()`, and `dpaa2_mac_set_supported_interfaces()`. Statistics use arrays of `struct dpmac_counter` mapping DPMAC counter IDs to either ethtool string names or offsets in standard ethtool stats structures. Newer firmware uses DMA-backed bundled reads prepared by `dpaa2_mac_setup_stats()` and consumed by `dpaa2_mac_get_standard_stats()` or `dpaa2_mac_get_ethtool_stats()`, while older firmware falls back to `dpmac_get_counter()` per counter.

## Control flow
`dpaa2_mac_open()` opens the DPMAC object, reads attributes and API version, detects features, finds the firmware node, links the netdev OF node, and allocates DMA buffers for supported stats bundles. `dpaa2_mac_connect()` validates interface mode, optionally obtains a SerDes PHY when protocol changes are supported, rejects fixed-link RGMII delay modes that the MAC cannot provide, creates PCS for non-RGMII PHY/backplane modes, initializes phylink capabilities and supported interfaces, creates phylink, and connects the firmware PHY. `dpaa2_mac_start()` powers SerDes and starts phylink under RTNL; `dpaa2_mac_stop()` stops phylink and powers SerDes off. Disconnect reverses phylink, PCS, and SerDes references. Close releases stats DMA buffers, closes DPMAC, and drops the firmware-node reference.

## State and persistence behavior
State lives in `struct dpaa2_mac`: MC device/handle, DPMAC attributes, API version, feature bits, current `dpmac_link_state`, phylink objects, selected interface mode, optional PCS, firmware node, optional SerDes PHY, and DMA buffers for stats. Link state is pushed into MC firmware by phylink callbacks but is not durable across object reset. Stats buffers are noncoherent DMA allocations and must be synchronized before and after MC statistics calls.

## Dependencies and integration points
This file depends on fsl-mc DPMAC commands, Linux phylink, PHY/SerDes APIs, Lynx PCS, OF/ACPI firmware properties, and ethtool standard stats structures. It is used by `dpaa2-eth.c` and switch support to manage physical endpoints and gather MAC counters.

## Risks and edge cases
Firmware-node discovery can defer probe if the parent DPRC fwnode is not ready. PCS lookup permits old DTs without `pcs-handle` but treats unavailable or failed PCS nodes differently. SerDes PHY is only attempted for OF nodes and non-RGMII modes when protocol change is supported. `dpaa2_mac_config()` changes both DPMAC protocol and SerDes mode at runtime, so ordering and error reporting matter. Stats paths must handle missing DMA buffers or unsupported feature bits and fall back cleanly. `dpaa2_mac_disconnect()` uses RTNL while disconnecting the PHY, so callers must avoid lock inversions.

## Test signals
Probe DPMAC endpoints with OF and ACPI descriptions, fixed link, external PHY, backplane, PCS-backed SGMII/1000BASE-X, and SerDes protocol-change-capable hardware. Exercise link up/down, pause negotiation, ethtool link settings, module unload/reload, endpoint hot changes, and both bundled and fallback stats retrieval. Fault injection around missing `pcs-handle`, deferred PCS/SerDes, and `dpmac_get_statistics()` should not leak DMA buffers or firmware-node references.
