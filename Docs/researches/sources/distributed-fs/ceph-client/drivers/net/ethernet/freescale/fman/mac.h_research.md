# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/mac.h

## Purpose
Defines the generic FMan MAC device abstraction shared by FMan MAC backends and the DPAA Ethernet netdev layer.

## Important APIs, Types, and Functions
`struct mac_device` holds mapped MAC registers, device/resource pointers, MAC address, two FMan ports, phylink state/config, PHY interface, multicast/promiscuous flags, backend operation callbacks, ethtool statistic callbacks, speed update callback, backend `fman_mac` private pointer, and references to parent FMan/port devices. It also defines `PORT_NUM`, `fman_config_to_mac`, and `struct dpaa_eth_data`.

## Control Flow and State
The only executable logic is the inline `fman_config_to_mac` container conversion. Runtime state is owned by `mac.c`, individual backends, and DPAA Ethernet users through the operation pointers and fields in `mac_device`.

## Dependencies and Integration Points
Includes Linux device, Ethernet, PHY, phylink, and list headers plus `fman_port.h`, `fman.h`, and `fman_mac.h`. It is the key contract between generic MAC probing, dTSEC/TGEC/MEMAC implementations, and the `dpaa-ethernet` child driver.

## Risks and Test Signals
Risks include callback signature drift, missing backend operations, stale `fman_mac` private pointers, and assumptions that exactly two FMan ports exist. Test signals are compile coverage for all FMan backends and runtime DPAA Ethernet operations for link, multicast, timestamping, ethtool stats, and speed updates.
