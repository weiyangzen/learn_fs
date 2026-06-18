# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/lan969x/lan969x_rgmii.c

## Purpose
This file configures LAN969x RGMII MAC-side behavior for ports 28 and 29. It programs TX clock frequency, MAC speed, IFG, VLAN tag awareness, optional internal RX/TX delay lines, GPIO muxing, and MAC enablement.

## Important APIs, Types, And Functions
The exported function is `lan969x_port_config_rgmii()`. Internal helpers map speed to clock selectors and device speed selectors, validate delay properties in picoseconds, program `HSIO_WRAP_RGMII_CFG`, `DEVRGMII_*`, `HSIO_WRAP_DLL_CFG`, and `HSIO_WRAP_XMII_CFG`.

## Control Flow
Configuration first reads `rx-internal-delay-ps` and `tx-internal-delay-ps` from the port device node and maps allowed values to hardware selectors. It enables DLLs, enabling the delayed clock only when delay is nonzero. Then it releases RGMII clock resets and selects TX clock rate from link speed, enables GPIO RGMII muxing, enables RX/TX MAC, configures IFG, selects device speed, and programs VLAN tag parsing based on the port VLAN type and maximum tag count.

## State And Persistence
Runtime state is hardware register configuration derived from `struct sparx5_port`, `struct sparx5_port_config`, and device-tree delay properties. Settings persist in hardware until reconfigured or reset.

## Dependencies And Integration Points
The file integrates with phylink-driven port configuration through `sparx5_ops.port_config_rgmii`, with OF properties on each port node, and with Sparx5 VLAN state (`vlan_type`, `custom_etype`, `max_vlan_tags`).

## Risks And Edge Cases
Only exact delay values 0, 1000, 1700, 2000, 2500, 3000, and 3300 ps are accepted. `RGMII_PORT_IDX()` assumes only ports 28 and 29 call this path. `HSIO_WRAP_XMII_CFG(!idx)` is a compact mapping that should be checked against hardware docs. The comments distinguish MAC-side delay properties from PHY-mode delay semantics, so duplicate PHY and MAC delays are a board-design risk.

## Test Signals
Bring up 10/100/1000 Mbps RGMII links on ports 28/29, test each supported internal delay value, verify VLAN tagged and untagged traffic, confirm GPIO mux selection, and inspect invalid delay extents returning `-EINVAL`.
