# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_new.c

## Purpose
`cpsw_new.c` is the newer CPSW switchdev-capable platform driver. It supports `ti,*-cpsw-switch` compatibles, creates per-port netdevs from `ethernet-ports`, can operate in dual-MAC or switch mode, registers switchdev and netdevice notifiers, and exposes devlink runtime parameters for `switch_mode` and `ale_bypass`.

## Important APIs, Types, And Functions
The platform driver is `cpsw_driver` named `cpsw-switch`. Netdev operations mirror the legacy driver but add `ndo_get_phys_port_name`, `ndo_get_port_parent_id`, immutable netns, and hardware TC feature advertising. `struct cpsw_devlink` binds devlink to `struct cpsw_common`. Devlink handlers `cpsw_dl_switch_mode_get/set()` and `cpsw_dl_ale_ctrl_get/set()` manage switch mode and ALE bypass. Notifier helpers `cpsw_register_notifiers()`, `cpsw_netdevice_event()`, `cpsw_netdevice_port_link()`, and `cpsw_netdevice_port_unlink()` connect bridge membership to switchdev offload tracking. Port setup flows through `cpsw_create_ports()`, `cpsw_register_ports()`, and `cpsw_slave_open()`.

## Control Flow
Probe allocates common state and two slave slots, maps subsystem registers, gets named IRQs, enables runtime PM, parses `ethernet-ports`, initializes common CPSW resources, creates base CPDMA channels, creates per-port netdevs, requests IRQs, registers switchdev/netdevice notifiers, registers devlink params, then registers netdevs. Opening a port resumes PM, configures queues, initializes the host port once, opens that slave, creates/fills shared RX pools if first user, registers CPTS, enables NAPI/IRQs, restores VLAN/QoS/clsflower offload, starts CPDMA, and increments usage. Switch mode changes under RTNL either update stored mode/port VLANs while all ports are down or, while running, temporarily enables ALE bypass, clears ALE, reinitializes host mode, rebuilds per-port ALE entries, updates `tx_packet_min`, and disables bypass. Bridge upper events record a single hardware bridge device and update `offload_fwd_mark` when both ports are offloaded.

## State And Persistence
The core mode bit is still `cpsw->data.dual_emac`; `cpsw_is_switch_en()` returns its inverse. Per-port state includes `emac_port` values 1 and 2, `tx_packet_min`, offload forward mark, reserved dual-EMAC VLANs, and bridge membership. Device-wide state includes devlink pointer, ALE bypass flag, base MAC for parent ID, `br_members`, and `hw_bridge_dev`. Runtime switch transitions persist by rewriting ALE entries and port VLANs rather than rebooting the driver.

## Dependencies And Integration Points
This file integrates CPSW with devlink, switchdev, bridge upper-device notifiers, phylib, of_platform population, CPDMA, ALE, CPGMAC sliver, CPTS, XDP/page_pool, ethtool shared helpers, and Linux netdevice APIs. It depends on `cpsw_switchdev.c` for VLAN/MDB/FDB/STP object handling.

## Risks
Runtime switch-mode transitions are complex: a bad ordering around ALE bypass, table clear, `dual_emac` flip, port VLAN rewrite, or `tx_packet_min` update can leak traffic across ports or break bridge forwarding. `cpsw_dl_ale_ctrl_set()` returns 0 even when `cpsw_ale_control_set()` fails after assigning `ret`, which hides errors. `cpsw_port_offload_fwd_mark_update()` assumes every slave has an `ndev` before calling `netdev_priv()`. Only one hardware bridge is supported. New DT parsing requires exactly two port children and valid PHY nodes for enabled ports, unlike older legacy binding flexibility.

## Test Signals
Test probe with `ti,cpsw-switch` DT, disabled port nodes, named IRQs, fixed-link and PHY-handle ports, netdev registration order, devlink `switch_mode` toggles with ports down and up, bridge enslave/release of one and both ports, rejection of second bridge, `ale_bypass` toggles, VLAN and multicast behavior in switch versus dual-MAC mode, XDP, PTP timestamping, suspend/resume, and offload forward mark behavior with bridge traffic.
