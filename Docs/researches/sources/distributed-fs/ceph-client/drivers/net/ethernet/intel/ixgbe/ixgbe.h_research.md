# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe.h

## Purpose
`ixgbe.h` is the central private header for the ixgbe driver. It defines descriptor limits, buffer sizing, TX/RX flags, VF and SR-IOV state, ring and queue-vector structures, adapter-wide state, feature flags, helper macros, inline packet timestamp handling, and prototypes for the driver's cross-file implementation.

## Important APIs, Types, and Functions
Key structures include `struct ixgbe_adapter`, `struct ixgbe_ring`, `struct ixgbe_q_vector`, `struct ixgbe_tx_buffer`, `struct ixgbe_rx_buffer`, `struct vf_data_storage`, `struct ixgbe_ring_feature`, and `struct ixgbe_fdir_filter`. It defines feature bits in `adapter->flags` and `flags2`, ring state bits, queue limits, RSS/VMDQ/FDIR constants, XDP helpers, PTP fields, devlink region fields, and many exported driver prototypes. Inline helpers include descriptor accessors, buffer sizing, ring-state tests, `ixgbe_from_netdev()`, XDP queue selection, max RSS indices, `ixgbe_ptp_rx_hwtstamp()`, and `ixgbe_enabled_xdp_adapter()`.

## Control Flow
The header's inline control flow is focused on fast-path decisions: RX buffer size/page order selection based on ring state, descriptor availability calculation, XDP ring selection based on CPU/static key, MAC-type-based RSS limit selection, and RX hardware timestamp dispatch depending on descriptor status bits.

## State and Persistence Behavior
Most ixgbe runtime state is shaped here. `struct ixgbe_adapter` persists for the PCI function lifetime and tracks netdev, PCI, devlink, rings, queues, interrupts, DCB, SR-IOV, PTP, FDIR, XDP, IPsec, firmware flags, statistics, and hardware state. The header does not itself persist state, but its structures mirror hardware settings and hold software-owned counters and references.

## Dependencies and Integration Points
It includes kernel PCI/netdev/PTP/devlink/XDP headers and ixgbe type/common/DCB/E610/IPsec/FCoE headers. It is included by almost every ixgbe source file and forms the contract between probe, TX/RX, ethtool, devlink, PTP, SR-IOV, DCB, FCoE, IPsec, XSK, and MAC-specific modules.

## Risks and Edge Cases
This header has high blast radius. Layout changes to hot ring structures can affect cache alignment and fast path performance. Feature bit semantics must stay synchronized with implementation files. Inline timestamp handling mutates per-ring timestamp watchdog state and must match PTP register behavior. XDP queue selection depends on static key state and CPU indexes. Conditional FCoE/IPsec/debugfs/hwmon declarations must match Makefile objects and stubs.

## Test Signals
Full ixgbe build matrix across optional features, sparse/smatch for structure/inline misuse, RX/TX performance smoke tests, PTP timestamp tests, SR-IOV VF lifecycle, XDP/AF_XDP, DCB/FCoE/IPsec feature builds, and probe/remove with devlink region fields initialized and destroyed.
