# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/lio_vf_rep.c

## Purpose
Implements switchdev VF representor netdevices for LiquidIO PF mode. Each representor exposes a VF as a Linux netdev when the adapter is in switchdev eswitch mode, allowing control-plane operations and packet forwarding through firmware.

## Important APIs, Types, and Functions
The exported lifecycle functions are `lio_vf_rep_create`, `lio_vf_rep_destroy`, `lio_vf_rep_modinit`, and `lio_vf_rep_modexit`. Netdev operations are in `lio_vf_rep_ndev_ops`: `lio_vf_rep_open`, `lio_vf_rep_stop`, `lio_vf_rep_pkt_xmit`, `lio_vf_rep_tx_timeout`, `lio_vf_rep_phys_port_name`, `lio_vf_rep_get_stats64`, `lio_vf_rep_change_mtu`, and `lio_vf_get_port_parent_id`. Firmware commands are wrapped by `lio_vf_rep_send_soft_command` using `OPCODE_NIC_VF_REP_CMD`. Packet receive and transmit paths use `lio_vf_rep_pkt_recv`, `lio_vf_rep_copy_packet`, `lio_vf_rep_pkt_xmit`, and `lio_vf_rep_packet_sent_callback`.

## Control Flow
Creation first checks `DEVLINK_ESWITCH_MODE_SWITCHDEV` and SR-IOV enablement, then allocates one Ethernet device per VF, assigns an ifindex of `pf_num * 64 + vf + 1`, sets MTU bounds and netdev ops, registers the device, starts a delayed stats poll, and registers a dispatch handler for `OPCODE_NIC_VF_REP_PKT`. Open and stop send firmware state changes before toggling local carrier and queue state. TX validates the representor state, uses the parent PF netdev queue, maps the SKB linearly, prepares an `OPCODE_NIC_VF_REP_PKT` soft command with the representor ifidx, and frees the SKB in the callback. RX maps the firmware-provided ifidx from the response header to a representor netdev, copies or attaches page-backed data into the SKB, strips Octeon data header bytes, and injects it with `netif_rx`.

## State and Persistence Behavior
Per-representor state lives in `struct lio_vf_rep_desc`: parent netdev, representor netdev, Octeon device, stats snapshot, delayed work, atomic ifstate, and firmware ifidx. The Octeon device owns `vf_rep_list.ndev[]` and `num_vfs`. Firmware stores representor state, MTU, device name, and stats; the driver periodically refreshes stats and swaps TX/RX values when exposing them because a representor is a switch port.

## Dependencies and Integration Points
Depends on Linux netdevice notifier APIs, devlink eswitch mode, SR-IOV state, DMA mapping, SKB helpers, and LiquidIO soft-command, dispatch, network, and common ABI headers. It integrates with firmware through `lio_vf_rep_req` and `lio_vf_rep_resp`, and with the parent PF through `oct->props[0].netdev` and the parent's TX queue.

## Risks
The code supports only single-buffer representor packets on TX and rejects fragmented SKBs, so feature flags must not promise SG offload. The stats work reschedules itself unconditionally and must be cancelled before unregister/free. If dispatch registration fails after some netdevs were registered, cleanup must unwind all delayed work and devices. Ifidx arithmetic is tightly coupled to `CN23XX_MAX_VFS_PER_PF` and the firmware convention. Name sync rejects names longer than `LIO_IF_NAME_SIZE`, and soft-command ownership relies on `caller_is_done`.

## Test Signals
Test switchdev transition with SR-IOV enabled and disabled, representor create/destroy for multiple VFs, open/stop state commands, MTU changes, netdev rename sync, stats polling, representor TX/RX traffic, queue full and callback wakeup paths, fragmented SKB rejection, port-name strings like `pf0vf0`, parent-id reporting, and cleanup while stats work or firmware commands are pending.
