# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx_fw.c

Purpose: firmware-command layer over the rnpgbe mailbox transport. It builds packed firmware request/reply structs for hardware info, power state, reset, and MAC address commands.

Important functions: `mucse_fw_send_cmd_wait_resp` serializes request/response commands under `hw->mbx.lock`. Public wrappers are `mucse_mbx_sync_fw`, `mucse_mbx_powerup`, `mucse_mbx_reset_hw`, and `mucse_mbx_get_macaddr`; internal `mucse_mbx_get_info` stores the PF/VF number returned by firmware.

Control flow: request/response commands write the request, wait for firmware ack, then poll/read replies up to three attempts until opcode matches. Nonzero reply error codes become `-EIO`; opcode mismatch after retries becomes `-ETIMEDOUT`. Sync retries hardware-info requests on timeout. Power-up sends only the request and waits for ack, not a full reply.

State and persistence: mutates `hw->pfvfnum` after `GET_HW_INFO`. Power-up/power-down and reset affect firmware/hardware state. No persistent host storage.

Dependencies and integration: depends on packed structs and opcodes from `rnpgbe_mbx_fw.h`, raw transport from `rnpgbe_mbx.c`, endian helpers, and Ethernet address copying by chip code.

Risks: `reply->opcode` and `reply->error_code` are little-endian fields but are compared/read directly in places; this is harmless only on little-endian hosts or if firmware/native layout matches. The retry loop permits four reads because it decrements after the condition. `mucse_mbx_get_macaddr` trusts `port` as an index into four reply addresses.

Test signals: command success/failure for `GET_HW_INFO`, `POWER_UP`, `RESET_HW`, `GET_MAC_ADDRESS`; endian/static analysis; timeout injection; invalid port/port-mask responses; and verify `pfvfnum` feeds MAC request.
