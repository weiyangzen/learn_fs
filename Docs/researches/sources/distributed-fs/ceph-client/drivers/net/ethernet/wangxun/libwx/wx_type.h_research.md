# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/wangxun/libwx/wx_type.h

## Purpose
`wx_type.h` is the central shared hardware and software data model for Wangxun Ethernet drivers. It defines register offsets, bitfields, descriptors, packet type decoding constants, mailbox/host-interface command structures, queue/ring structures, statistics, PF/VF state, feature flags, and MMIO access helpers consumed by PF and VF drivers.

## Important APIs, Types, and Functions
Key data types include `struct wx`, `struct wx_ring`, `struct wx_q_vector`, `struct wx_ring_container`, `struct wx_mbx_info`, `struct wx_mac_info`, `struct wx_eeprom_info`, `struct vf_data_storage`, `struct vf_macvlans`, descriptor unions `wx_tx_desc`/`wx_rx_desc`, `struct wx_tx_buffer`, `struct wx_rx_buffer`, and PTP/statistics containers. Enumerations classify MAC/media/eeprom/reset/flow-control/state/flag/ring-feature values. Inline helpers include `rd32m()`, `wr32m()`, `rd64()`, `rd32ptp()`, `wr32ptp()`, `rd32_wrap()`, `phylink_to_wx()`, and `wx_rx_pg_order()`.

## Control Flow
The header has no standalone control flow, but it defines the state and register vocabulary used by all control paths. PF probe initializes `struct wx`, reset paths program registers defined here, fast paths consume descriptor and ring definitions, PTP uses timestamp register wrappers, and SR-IOV/VF paths use `vf_data_storage` and mailbox constants.

## State and Persistence Behavior
Most state is memory-resident driver state with device lifetime or netdev-open lifetime. Hardware register definitions map to persistent device state until reset or power cycle. `struct wx` is the aggregation point for PCI/MMIO identity, link state, phylink/PTP, queue arrays, MSI-X vectors, RSS, MAC/VLAN filters, SR-IOV VF data, Flow Director callbacks, and service work. There is no filesystem persistence.

## Dependencies and Integration Points
The header depends on Linux networking, VLAN, phylink, PTP, DIM, bitfield, and IP headers. It integrates every Wangxun module in this subset: `libwx` hardware/mailbox/library code, `ngbe`, `ngbevf`, and `txgbe`. Its MMIO macros assume `wx->hw_addr` has been ioremapped and that callers provide required locking around shared hardware access.

## Risks and Edge Cases
Because this is a broad register contract, incorrect masks or offsets affect many features. `struct wx` mixes PF-only and VF-only fields; call sites must respect device mode. Fixed queue arrays sized to 64 require queue count validation. `rd32ptp()`/`wr32ptp()` apply a MAC-type offset that must match hardware generation. VF state is indexed by `num_vfs`, so SR-IOV teardown must clear `num_vfs` before freeing `vfinfo`.

## Test Signals
Compile all Wangxun drivers using the header, run sparse/lockdep/bounds checks on ring and VF indexes, exercise reset/open/close/PTP/SR-IOV paths, and verify descriptor layout and register offsets against hardware documentation or working silicon. Endianness-sensitive descriptor and host-interface structures need packet-path and firmware-command tests on little-endian systems.
