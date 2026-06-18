# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_priv.h

## Purpose
`cpsw_priv.h` is the central private interface for CPSW drivers. It defines hardware offsets, feature bits, constants, register layouts, platform data, slave/common/private state structures, logging macros, XDP metadata helpers, and prototypes shared between legacy, switchdev, ethtool, ALE, and helper implementation files.

## Important APIs, Types, And Functions
Important structures are `struct cpsw_platform_data`, `struct cpsw_slave_data`, `struct cpsw_slave`, `struct cpsw_vector`, `struct cpsw_common`, `struct cpsw_priv`, `struct cpsw_ale_ratelimit`, `struct addr_sync_ctx`, and `struct cpsw_meta_xdp`. It defines CPSW version constants, register offsets for v1/v2 layouts, CPDMA offsets, VLAN and FIFO constants, timestamp-control masks, queue limits, descriptor defaults, and XDP handle tagging helpers (`cpsw_is_xdpf_handle()`, `cpsw_xdpf_to_handle()`, `cpsw_handle_to_xdpf()`). It declares all shared helper APIs implemented in `cpsw_priv.c` and `cpsw_ethtool.c`.

## Control Flow
The header has no runtime control flow, but its macros and inline helpers drive key flows: `ndev_to_cpsw()` and `napi_to_cpsw()` convert kernel callback objects to driver common state; `slave_read()`/`slave_write()` centralize slave MMIO access; XDP handle tagging lets TX completion choose skb or XDP cleanup path.

## State And Persistence
`struct cpsw_common` persists device-wide state: mapped registers, version, DMA, ALE, CPTS, IRQs, page pools, queues, bridge/devlink state, and resource counts. `struct cpsw_priv` persists per-netdev state: MAC, pause flags, QoS settings, timestamp flags, XDP program/RXQs, port id, offload mark, packet minimum, rate-limit cookies, and rx-mode work. `struct cpsw_slave` persists per-port register base, PHY/sliver, MAC control, netdev, and VLAN.

## Dependencies And Integration Points
It includes XDP/BPF UAPI and `davinci_cpdma.h`, and is included by almost every CPSW source in this subset. It provides the contract between Linux netdev callbacks, CPDMA callbacks, ALE programming, phylib, CPTS, TC, XDP, and ethtool.

## Risks
Because this header exposes many hardware constants and shared structures, changes have broad blast radius. Field ownership is split across files; for example, `usage_count`, page pools, and queue counts are modified from open/stop and ethtool paths. Inline XDP pointer tagging relies on alignment and low-bit availability. Register offsets must remain correct for CPSW v1/v2 layouts. `cpsw_slave_index` is an external function pointer rather than a fixed helper, so callers depend on front-end driver initialization.

## Test Signals
Compile coverage across both `cpsw` and `cpsw-switch` drivers is essential. Runtime tests should cover state transitions that touch shared fields: dual-port open/close, channel changes, XDP attach/detach, switchdev bridge offload, hardware timestamping, QoS restore, and register writes for v1 and v2 CPSW versions.
