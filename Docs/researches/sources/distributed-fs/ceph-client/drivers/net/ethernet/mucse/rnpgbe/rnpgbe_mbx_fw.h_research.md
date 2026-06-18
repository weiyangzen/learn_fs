# sources/distributed-fs/ceph-client/drivers/net/ethernet/mucse/rnpgbe/rnpgbe_mbx_fw.h

Purpose: firmware mailbox ABI definitions for rnpgbe.

Important declarations: `MUCSE_MBX_REQ_HDR_LEN`, opcodes `GET_HW_INFO`, `GET_MAC_ADDRESS`, `RESET_HW`, and `POWER_UP`; packed `struct mucse_hw_info`, `struct mbx_fw_cmd_req`, and `struct mbx_fw_cmd_reply`; prototypes for firmware command helpers.

Control flow: no executable flow. The request union carries power-up and MAC-address payloads; the reply union carries raw data, MAC address arrays, or hardware info.

State and persistence: ABI structs define transient mailbox messages. Fields like `fw_version`, `pfnum`, and MAC addresses describe firmware/device state consumed during probe.

Dependencies and integration: includes Linux types and `rnpgbe.h`. Used by `rnpgbe_mbx_fw.c`, `rnpgbe_chip.c`, and `rnpgbe_main.c`.

Risks: packed ABI must match firmware exactly. Endianness annotations require callers to use `cpu_to_le*`/`le*_to_cpu`; direct comparisons are a review hotspot. The MAC reply supports four ports, so port validation must happen before indexing.

Test signals: compile-time struct size checks if added, firmware round-trip tests, endian sparse warnings, and MAC/hardware-info decoding on all supported boards.
