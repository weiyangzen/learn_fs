# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep_vf/octep_vf_mbox.c

## Purpose
This file implements the VF side of the PF/VF mailbox protocol. It sets up mailbox registers, negotiates protocol version, sends synchronous commands to PF, performs fragmented bulk reads for link info and stats, applies mailbox-backed netdev operations, processes PF link notifications, and notifies PF on VF removal.

## Important APIs, Types, And Functions
- Lifecycle: `octep_vf_setup_mbox()` allocates mailbox state, binds chip-specific registers, initializes work, and sets initial negotiated version; `octep_vf_delete_mbox()` cancels work and frees it.
- Version and async work: `octep_vf_mbox_version_check()` negotiates with PF; `octep_vf_mbox_work()` processes PF-to-VF notifications, currently link-status changes.
- Command core: `__octep_vf_mbox_send_cmd()` writes a command word and polls for PF response; `octep_vf_mbox_send_cmd()` serializes commands and checks version support.
- Bulk reads: `octep_vf_mbox_bulk_read()` sends an initial request to get payload length and then reads six-byte fragments into `mbox_data.recv_data`.
- Netdev helpers: `octep_vf_mbox_set_mtu()`, `octep_vf_mbox_set_mac_addr()`, `octep_vf_mbox_get_mac_addr()`, `octep_vf_mbox_set_rx_state()`, `octep_vf_mbox_set_link_status()`, `octep_vf_mbox_get_link_status()`, `octep_vf_mbox_dev_remove()`, `octep_vf_mbox_get_fw_info()`, and `octep_vf_mbox_set_offloads()`.

## Control Flow
Probe sets up the mailbox before registering the netdev. Commands are serialized with `mbox->lock`; the VF writes a command word to `mbox_write_reg`, then polls the same register until PF overwrites it with a different word. ACK/NACK type bits determine success. Bulk reads first get total length from PF, then repeatedly set `frag=1` and copy up to six bytes from each response into the local receive buffer.

PF notifications are delivered by chip-specific interrupt handlers scheduling `octep_vf_mbox_work()`. The worker reads `mbox_read_reg`, decodes the notification opcode, and updates `link_info.oper_up` plus carrier state for link-status notifications.

## State And Persistence
Runtime state includes `oct->mbox`, mailbox register pointers, `mbox_neg_ver`, `mbox_data.data_index`, `mbox_data.recv_data`, and `oct->fw_info` fetched from PF. PF-side persistent-ish runtime state is changed by commands for MAC, MTU, Rx/link status, offloads, and VF removal, but no disk state is written.

## Dependencies And Integration Points
This file depends on `octep_vf_main.h`, `octep_vf_config.h`, Linux PCI/netdevice/workqueue APIs, and a PF implementing the mirrored protocol. It is called by VF probe, open/stop, netdev MAC/MTU/features operations, ethtool stats/link functions, and remove.

## Risks And Edge Cases
- The command timeout is `8000` polls with 1-1.5 ms sleeps, so a wedged PF can stall operations for seconds.
- Bulk receive buffer is 320 bytes, while PF-side maximum is 384 bytes; large stat/link payload growth can overflow or truncate unless both sides are updated.
- `octep_vf_mbox_set_mtu()` validates frame size against `ETH_MAX_MTU`, which may be lower than the driver's advertised VF max frame intent.
- `octep_vf_mbox_set_offloads()` checks `rsp.s_link_state.type` rather than `rsp.s_offloads.type`; the bitfield location is equivalent for type, but the member choice is misleading.
- Commands without a response, such as device remove, return immediately after writing; PF acknowledgement is not verified.

## Test Signals
Test PF/VF version negotiation, every mailbox command ACK/NACK path, timeout behavior with PF unavailable, link notification carrier changes, bulk stats and link-info reads, MAC and MTU changes from VF, offload feature changes, VF remove notification, and concurrent ethtool/netdev requests for mutex serialization.
