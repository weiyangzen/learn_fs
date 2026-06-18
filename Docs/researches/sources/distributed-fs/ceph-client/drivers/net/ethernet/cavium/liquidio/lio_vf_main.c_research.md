# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_main.c

## Purpose
Implements the PCI and `net_device` driver for the LiquidIO CN23xx virtual function. It probes VF PCI functions, initializes Octeon device state, negotiates PF/VF handshaking, creates the VF NIC interface, maps Linux transmit/receive operations to Octeon IQ/DROQ queues, and tears the device down on remove or fatal PCI error.

## Important APIs, Types, and Functions
Top-level integration is through `liquidio_vf_pci_driver`, `liquidio_vf_probe`, `liquidio_vf_remove`, `liquidio_vf_init`, and `liquidio_vf_exit`. Device bring-up is sequenced by `octeon_device_init`, which calls PCI setup, CN23xx VF register setup, dispatch setup, soft-command pool setup, IQ/DROQ setup, mailbox setup, MSI-X vector setup, PF/VF handshake, queue enable, initial OQ credits, and `liquidio_init_nic_module`. Netdev operations are collected in `lionetdevops`: open, stop, xmit, stats, MAC, multicast, VLAN filters, MTU, feature changes, and hardware timestamp get/set. Important helpers include `setup_nic_devices`, `send_rx_ctrl_cmd`, `lio_nic_info`, `update_link_status`, `liquidio_xmit`, `send_nic_timestamp_pkt`, and the SKB/gather cleanup callbacks.

## Control Flow
Probe allocates an `octeon_device`, stores it as PCI driver data, fills PCI identity fields, then runs the staged Octeon initialization. `setup_nic_devices` sends `OPCODE_NIC_IF_CFG` to firmware, receives queue masks, link info, MAC, and firmware version, allocates an Ethernet device, installs operations and ethtool hooks, sets offload features, creates IO queues and gather lists, registers the netdev, and enables default tunnel checksum features. Open enables NAPI, marks the interface running, starts TX queues, schedules stats work, and sends an RX start command. Stop sends RX stop, drops carrier, waits for RX drain, disables NAPI, re-enables the DROQ tasklet path, and cancels stats work. TX maps linear or SG SKB data for DMA, constructs Octeon command fields, handles checksum, VLAN, GSO, VXLAN, and TX timestamp flags, then sends a no-response or response soft command.

## State and Persistence Behavior
State is in `octeon_device` status bits, `oct->props[]`, queue masks, interrupt vectors, PF/VF handshake fields, and per-interface `struct lio` fields such as `ifstate`, `linfo`, `intf_open`, queue indices, feature capability masks, gather lists, and delayed work. Persistent external state is firmware-owned: link state, MAC permission, queue assignment, LRO/checksum/VXLAN/VLAN settings, RX forwarding state, and timestamps are communicated through Octeon commands. Removal uses the status machine in `octeon_destroy_resources` to unwind only the stages that were reached.

## Dependencies and Integration Points
Depends on Linux PCI, AER, MSI-X, netdevice, NAPI, VLAN, UDP tunnel, hardware timestamping, DMA mapping, and workqueue APIs. Driver-internal dependencies include `liquidio_common.h`, `octeon_droq.h`, `octeon_iq.h`, `response_manager.h`, `octeon_device.h`, `octeon_nic.h`, `octeon_network.h`, and `cn23xx_vf_device.h`. Firmware integration is through `OPCODE_NIC` soft commands and dispatch callbacks for `OPCODE_NIC_INFO`.

## Risks
The highest-risk code is lifecycle ordering: interrupts and queues are enabled before packets can arrive, and teardown must avoid freeing queues, IRQs, NAPI, tasklets, or soft commands while work is in flight. TX error paths can leak DMA mappings or gather-list entries if changed carelessly. `setup_nic_devices` has several partial-failure exits and relies on `caller_is_done` for soft-command ownership. Link-MTU changes run through a workqueue under RTNL. The AER path forcibly completes pending requests and disables PCI, so recovery behavior is intentionally limited for fatal errors.

## Test Signals
Useful signals include VF probe/remove, module load/unload, PF/VF handshake success, MSI-X vector allocation and affinity cleanup, netdev registration, interface up/down with RX start/stop commands, queue full and TX timeout behavior, linear and SG TX, TSO/TSO6, VLAN tag insertion and filtering, VXLAN tunnel port add/delete, RX checksum feature toggles, hardware TX/RX timestamping, link status updates including max-MTU reduction, AER nonfatal/fatal injection, and leak checks over failed init stages.
