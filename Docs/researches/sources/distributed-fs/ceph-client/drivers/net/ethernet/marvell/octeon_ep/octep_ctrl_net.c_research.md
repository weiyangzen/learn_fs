# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_net.c Research

## Purpose
`octep_ctrl_net.c` implements the Octeon EP network control protocol on top of the low-level control mailbox. It sends host-to-firmware commands for link status, RX state, MAC address, MTU, interface stats, link information, firmware info, device removal, and offloads; it also processes firmware responses and link notifications.

## Important APIs, Types, And Functions
Public APIs include `octep_ctrl_net_init()`, `octep_ctrl_net_get_link_status()`, `octep_ctrl_net_set_link_status()`, `octep_ctrl_net_set_rx_state()`, `octep_ctrl_net_get_mac_addr()`, `octep_ctrl_net_set_mac_addr()`, `octep_ctrl_net_get_mtu()`, `octep_ctrl_net_set_mtu()`, `octep_ctrl_net_get_if_stats()`, `octep_ctrl_net_get_link_info()`, `octep_ctrl_net_set_link_info()`, `octep_ctrl_net_recv_fw_messages()`, `octep_ctrl_net_get_info()`, `octep_ctrl_net_dev_remove()`, `octep_ctrl_net_set_offloads()`, and `octep_ctrl_net_uninit()`.

Internal helpers are `init_send_req()`, `octep_send_mbox_req()`, `process_mbox_resp()`, and `process_mbox_notify()`. The file maintains `ctrl_net_msg_id` and command-version tables for host-to-firmware and firmware-to-host commands.

## Control Flow
Initialization creates the response wait queue and wait list, fills `oct->ctrl_mbox` with current host protocol version and BAR memory from config, initializes the low-level mailbox, logs version ranges, and stores the firmware stats offset. Each get/set API builds a stack `octep_ctrl_net_wait_data`, initializes a mailbox request header and one SG buffer, fills a command-specific payload, sends it, and optionally waits up to 500 ms for a matching response.

`octep_send_mbox_req()` rejects commands outside the firmware-supported version interval, sends through `octep_ctrl_mbox_send()`, queues wait data on `oct->ctrl_req_wait_list` for synchronous requests, sleeps on `oct->ctrl_req_wait_q`, removes the wait-list node, and checks firmware reply status. `octep_ctrl_net_recv_fw_messages()` drains all currently available firmware messages; responses are copied into the matching wait-data object by message id, while notifications update netdev carrier state or forward VF notifications to PF/VF mailbox handling.

## State, Persistence, And Dependencies
State lives in `oct->ctrl_mbox`, `oct->ctrl_req_wait_q`, `oct->ctrl_req_wait_list`, `oct->ctrl_mbox_ifstats_offset`, cached `oct->link_info`, firmware stats fields, netdev carrier state, and the atomic message id. The protocol depends on `octep_ctrl_mbox`, firmware version compatibility, `octep_ctrl_net.h` ABI structures, wait queues, list operations, PCI/netdev logging, and PF/VF notification support.

## Integration Points
Main driver open/close/configuration paths use these APIs to synchronize MTU, MAC, link, RX state, offloads, firmware info, and device removal with firmware. Ettool uses link-info and stats commands. Chip-specific PF OEI interrupt handlers schedule control mailbox work, which calls `octep_ctrl_net_recv_fw_messages()`. PF/VF support receives VF notifications through `octep_pfvf_notify()`.

## Risks
The wait list is modified without an obvious local lock; correctness depends on serialization by caller/task context or external locking. `wait_event_interruptible_timeout()` returns negative on signal, but the code treats only `ret == 0 || ret == 1` as timeout-like and does not explicitly handle `ret < 0`, so interrupted waits can proceed to inspect an unset response. Message id masking uses `GENMASK(sizeof(msg_id) * BITS_PER_BYTE, 0)`, which requests one bit more than the 16-bit field width before assignment truncates. Version checks index command-version arrays by firmware-supplied or caller-filled command values, so invalid command values need bounds discipline.

## Test Signals
Test every get/set command against firmware versions 1.0.0 and 1.0.1 boundaries, synchronous response matching under concurrent requests, timeout and interrupted wait behavior, malformed response ids, firmware notifications for link up/down while netdev is running/stopped, VF-targeted notifications, mailbox receive drain loops, stats fetch failures, dev-remove during uninit with pending requests, and offload command rejection when firmware max version is below 1.0.1.
