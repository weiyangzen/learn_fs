# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_ctrl_net.h Research

## Purpose
`octep_ctrl_net.h` defines the host/firmware network-control protocol layered on the Octeon EP control mailbox. It enumerates commands, command directions, states, replies, request/response payloads, link/offload structures, max transfer union, wait-data storage, and public control-net APIs.

## Important APIs, Types, And Functions
Key enums are `octep_ctrl_net_cmd`, `octep_ctrl_net_state`, `octep_ctrl_net_reply`, `octep_ctrl_net_h2f_cmd`, and `octep_ctrl_net_f2h_cmd`. Request/response headers carry sender, receiver, command, and reply fields. Payload structs cover MTU, MAC address, link/RX state, link modes/autoneg/pause/speed, offloads, interface stats, and firmware info. `union octep_ctrl_net_max_data` sizes mailbox buffers for any protocol message. `struct octep_ctrl_net_wait_data` stores pending synchronous requests on a list with response data.

The declared API covers initialization, link status set/get, RX state, MAC set/get, MTU set/get, interface stats, link info set/get, firmware message receive, firmware info fetch, device removal notification, offload setting, and uninitialization.

## Control Flow
The header describes request/response shapes. Callers invoke the C implementation to build H2F requests and wait for H2F responses. Firmware can send F2H link-status notifications, which the implementation either applies to the PF netdev or forwards for VF handling.

## State, Persistence, And Dependencies
The protocol state persists in in-flight wait-data objects, firmware-visible command payloads, and cached device fields populated from responses. The header depends on `octep_cp_version.h`, firmware info from `octep_config.h` via included users, and statistics/link types from `octep_main.h` through C-file include order.

## Integration Points
Ettool depends on link info and interface stats types. Main netdev operations depend on MAC, MTU, link, RX state, offload, and device removal APIs. PF/VF mailbox code integrates through VF notification routing. The low-level mailbox uses the message sizes and buffers defined here as payloads.

## Risks
This is a packed firmware ABI. Field sizes, alignment, enum values, and command IDs must stay stable across host and firmware. The `link_info` structure uses 64-bit bitmaps internally, while ethtool code stores some fields in `u32`, so newly added high link-mode bits could be truncated. The wait-data object embeds list nodes and stack request/response storage, making lifetime correct only while synchronous waits remain active and properly removed.

## Test Signals
Validate structure sizes and offsets against firmware, command enum compatibility, max-data sizing, link mode bitmaps above 32 bits, VF id routing with `OCTEP_CTRL_NET_INVALID_VFID`, all public API payloads, async F2H link notification parsing, and wait-data cleanup during timeout and uninit.
