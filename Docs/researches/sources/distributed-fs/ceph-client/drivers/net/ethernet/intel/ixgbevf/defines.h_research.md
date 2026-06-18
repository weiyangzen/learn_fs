# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/defines.h

## Purpose
`defines.h` centralizes VF-side device IDs, link-speed values, descriptor layouts, descriptor status/error bits, queue limits, interrupt masks, RSS packet types, transmit offload command bits, DCA bits, and ixgbevf-local error codes. It is the low-level register/descriptor contract used by the VF driver.

## Important APIs, types, and constants
- Device IDs cover 82599, X540, X550, X550EM_x, X550EM_a, Hyper-V variants, and E610 VF IDs.
- `typedef u32 ixgbe_link_speed` plus 100M, 1G, and 10G link speed masks.
- Queue and descriptor constraints: max VF TX/RX queues, traffic classes, descriptor multiples, and buffer granularity.
- Descriptor structures: `union ixgbe_adv_tx_desc`, `union ixgbe_adv_rx_desc`, and `struct ixgbe_adv_tx_context_desc`.
- RX/TX status and command bits include checksum, VLAN, IPsec packet type/status, advanced descriptor type, TSO, context descriptor, payload length, and IPsec encryption flags.

## Control flow and integration
This header has no executable flow; it is consumed by VF data path, ethtool register dump/test code, RSS code, IPsec offload, and ring setup. Constants are used to interpret device writebacks and to construct transmit descriptors.

## State and persistence behavior
The header defines the shape of MMIO-visible and DMA-visible state. Hardware writes RX descriptor status/error/length/VLAN fields into memory matching these unions, and the driver writes TX descriptor command/address/context fields using these definitions.

## Dependencies
It depends on Linux integer/endian types and bit macros brought in by surrounding includes. It must stay consistent with hardware specifications and PF mailbox expectations.

## Risks
Incorrect bit masks or descriptor field definitions can corrupt DMA interpretation, break checksum/IPsec offloads, mis-detect packet types, or cause queue enablement failures. Duplicate macro names such as RX/TX enable masks intentionally match hardware concepts but require care during edits.

## Test signals
Compile coverage, ethtool register tests, normal RX/TX traffic, checksum offload validation, VLAN traffic, RSS hash reporting, IPsec descriptor offload, and descriptor ring wrap stress are the main validation paths.
