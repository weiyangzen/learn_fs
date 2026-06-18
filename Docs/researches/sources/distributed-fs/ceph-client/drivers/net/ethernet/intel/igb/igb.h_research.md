# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igb/igb.h

## Purpose
`igb.h` is the main private header for the Linux Intel igb driver. It centralizes driver constants, queue/ring data structures, adapter state, feature flags, inline helpers, and cross-file prototypes for the netdev data path, XDP/AF_XDP, PTP, ethtool, hwmon, filters, SR-IOV VF state, and hardware setup.

## Important APIs, Types, and Functions
Major types include `struct vf_data_storage`, `struct vf_mac_filter`, `struct igb_tx_buffer`, `struct igb_rx_buffer`, `struct igb_tx_queue_stats`, `struct igb_rx_queue_stats`, `struct igb_ring_container`, `struct igb_ring`, `struct igb_q_vector`, `struct hwmon_attr`, `struct hwmon_buff`, `struct igb_nfc_input`, `struct igb_nfc_filter`, `struct igb_mac_addr`, and `struct igb_adapter`. Important enums and flags include `enum igb_tx_flags`, `enum igb_tx_buf_type`, `enum e1000_ring_flags_t`, `enum igb_filter_match_flags`, `enum e1000_state_t`, adapter feature flags like `IGB_FLAG_HAS_MSIX`, `IGB_FLAG_EEE`, and `IGB_FLAG_RX_LEGACY`, plus PTP flags.

Inline helpers include RX buffer sizing and page order selection, descriptor status testing, descriptor unused calculation, PHY operation wrappers, XDP tail update, CPU-to-XDP TX ring mapping, and XDP enabled checks. The header also declares the major cross-file driver entry points such as `igb_open`, `igb_close`, `igb_up`, `igb_down`, `igb_reset`, queue resource setup/free/configure, stats update, ethtool ops setup, PTP hooks, hwmon init/exit, filter add/delete, and AF_XDP helpers.

## Control Flow
Most control flow is in static inline helpers. RX buffer sizing chooses 3K, build_skb, or 2K buffers based on page size and ring flags. `igb_desc_unused` computes ring free descriptors with wraparound. PHY wrappers no-op when the selected operation is absent, which simplifies callers but can hide missing initialization. `igb_xdp_ring_update_tail` asserts the TX queue lock, executes a write memory barrier, and writes the hardware tail pointer.

## State and Persistence
`struct igb_adapter` is the persistent per-device software state for the driver lifetime. It tracks netdev/pci handles, queue arrays, NAPI vectors, interrupt masks, timers, work items, rings, stats, hardware state (`struct e1000_hw`), VF data, RSS state, PTP clocks and timestamp state, firmware string, optional hwmon state, I2C adapter/client, EEE advertisement, NFC filter list, MAC filter table, and locks. Ring structures persist DMA descriptors, buffer info, queue indices, CBS/FQTSS settings, XDP program/pool links, and stats.

## Dependencies and Integration Points
The header includes `e1000_mac.h`, `e1000_82575.h`, Linux netdev/PCI/I2C/MDIO/PTP/XDP headers, and is included by most igb source files. It ties the low-level hardware layer to Linux subsystems: NAPI, ethtool, PTP clock, hwmon, I2C, SR-IOV, XDP, AF_XDP, VLAN, and traffic control offloads.

## Risks
Because this header defines shared state layout, changes have wide blast radius. Ring and adapter fields are touched from interrupt, NAPI, workqueue, ethtool, and netdev control paths, so locking and cacheline assumptions matter. Inline wrappers returning success when ops are missing can mask bugs. Queue count constants and fixed arrays must remain consistent with hardware limits and allocation code.

## Test Signals
Signals include clean builds across configs with and without `CONFIG_IGB_HWMON`, successful probe/open/close/reset, multiqueue TX/RX traffic, XDP and AF_XDP operation, ethtool stats and filter operations, PTP timestamping, SR-IOV VF behavior, and lockdep/KASAN/KCSAN runs around reset and queue reconfiguration.
