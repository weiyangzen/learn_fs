# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k.h

## Purpose
`fm10k.h` is the central private driver header for fm10k. It defines queue/ring data structures, interface state, feature flags, SR-IOV data, MAC/VLAN work items, fast-path helpers, and cross-file function prototypes.

## Important APIs, types, and functions
Important types include `struct fm10k_ring`, `fm10k_ring_container`, `fm10k_q_vector`, `fm10k_ring_feature`, `fm10k_iov_data`, `fm10k_macvlan_request`, and `struct fm10k_intfc`. It defines queue descriptor bounds, jumbo limits, ITR defaults, state/flag bit enums, TX/RX buffer structures, queue stat structures, ftag metadata, and skb control block layout. Inline helpers include mailbox locking, descriptor status testing, descriptor-unused calculation, and debug/DCB stubs when configs are disabled.

## Control flow
The header wires subsystem boundaries. PCI/probe code owns `fm10k_intfc`, netdev code owns ring resources and open/close, ethtool code reads and mutates rings/RSS/coalescing, IOV code manages VFs, and service/macvlan work uses state bits and workqueue declarations. Atomic bit flags coordinate reset, service scheduling, link state, stats updates, and MAC/VLAN work.

## State and persistence behavior
`struct fm10k_intfc` is the persistent per-device state: VLAN bitmap, netdev/pci pointers, rings, q_vectors, MSI-X entries, `iov_data`, hardware stats, mailbox lock, MMIO pointers, timers/work, RSS tables, encapsulation ports, MAC/VLAN queue, debugfs dentries, DCB pause state, GLORT resources, and VID. Rings persist DMA addresses, descriptor memory, counters, queue indexes, VLAN/QoS, and NAPI associations.

## Dependencies and integration points
The header includes Linux netdevice, PCI, VLAN, RCU, cpumask, and Ethernet helpers plus fm10k PF/VF hardware headers. It is included by essentially every fm10k source file and is the contract among main, PCI, netdev, ethtool, debugfs, DCB, and SR-IOV modules.

## Risks
Layout changes can affect cache alignment, fast-path performance, and assumptions in ethtool/debugfs/stat collection. State-bit changes can introduce reset/service races. `skb->cb` use must fit kernel skb control buffer constraints. Optional stubs must match real function signatures exactly. RCU-protected members such as L2 acceleration and `iov_data` need matching lifetime rules.

## Test signals
Compile coverage with optional configs, open/close stress, queue count changes, stats updates under traffic, SR-IOV enable/disable, debugfs entry lifecycle, DCB setup, RSS changes, and lockdep/RCU diagnostics are relevant signals.
