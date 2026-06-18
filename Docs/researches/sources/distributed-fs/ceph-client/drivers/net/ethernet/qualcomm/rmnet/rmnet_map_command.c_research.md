# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/rmnet/rmnet_map_command.c

Purpose: Handles MAP command frames, currently focused on modem-driven flow-control enable/disable commands for RMNET virtual devices.

Important APIs and functions: `rmnet_map_command()` is the public command dispatcher. `rmnet_map_do_flow_control()` validates mux id, resolves the endpoint, and calls `rmnet_vnd_do_flow_control()` on the virtual net_device. `rmnet_map_send_ack()` mutates the command type in-place and sends an ACK frame back through the real device's `ndo_start_xmit()`.

Control flow: The ingress handler routes command frames here only when ingress MAP commands are enabled. Command data follows the MAP header. Flow enable and disable commands call the VND queue wake/stop helper. Unsupported commands free the skb and report unsupported. Successful flow-control commands return ACK and reuse the original skb to send an acknowledgement. If CKSUMV4 ingress is enabled, ACK generation trims the downlink checksum trailer before transmit.

State and persistence: The command path changes the target VND TX queue state and mutates the command `cmd_type` for ACK. It does not store command history. It frees SKBs for invalid mux ids, missing endpoints, VND flow-control errors, or unsupported command names.

Dependencies and integration: Depends on endpoint lookup from `rmnet_config`, MAP structures from `rmnet_map.h`, and VND queue control from `rmnet_vnd.c`. ACK transmission directly calls the lower device `ndo_start_xmit()` under `netif_tx_lock()`.

Risks and test signals: Risks include short command frames not explicitly length-checked here, assumptions about skb linearity from the caller, and ACK reuse of the received skb. Tests should cover supported and unsupported command ids, invalid mux ids, endpoint absence, CKSUMV4 trailer trimming, and queue stop/wake effects on the VND.
