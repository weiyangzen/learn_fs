# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw.c

## Purpose

`fbnic_fw.c` implements the FBNIC host-to-firmware mailbox and TLV protocol handling. It initializes BAR4 mailbox descriptor rings, maps DMA-backed page messages, tracks completion slots, parses firmware responses, sends requests for capabilities, ownership, heartbeats, coredumps, firmware upgrades, QSFP EEPROM reads, thermal/voltage sensor reads, log streaming, and RPC MAC sync, and exposes a mailbox self-test. It is the central runtime bridge between the driver and management firmware.

## Important APIs, Types, And Functions

Mailbox lifecycle functions are `fbnic_mbx_init()`, `fbnic_mbx_clean()`, `fbnic_mbx_poll_tx_ready()`, `fbnic_mbx_poll()`, `fbnic_mbx_flush_tx()`, `fbnic_mbx_set_cmpl()`, and `fbnic_mbx_clear_cmpl()`. Low-level descriptor helpers include `__fbnic_mbx_wr_desc()`, `__fbnic_mbx_invalidate_desc()`, `__fbnic_mbx_rd_desc()`, and reset/clean/map/unmap helpers. DMA pages are tracked in `struct fbnic_fw_mbx::buf_info`.

Request transmitters include `fbnic_fw_xmit_test_msg()`, `fbnic_fw_xmit_ownership_msg()`, `fbnic_fw_xmit_coredump_info_msg()`, `fbnic_fw_xmit_coredump_read_msg()`, `fbnic_fw_xmit_fw_start_upgrade()`, `fbnic_fw_xmit_fw_write_chunk()`, `fbnic_fw_xmit_qsfp_read_msg()`, `fbnic_fw_xmit_tsene_read_msg()`, `fbnic_fw_xmit_send_logs()`, and `fbnic_fw_xmit_rpc_macda_sync()`. Completion allocation is provided by `__fbnic_fw_alloc_cmpl()`, `fbnic_fw_alloc_cmpl()`, and `fbnic_fw_put_cmpl()`.

Parser tables use `struct fbnic_tlv_index` arrays and `fbnic_fw_tlv_parser[]`. Notable parsers handle firmware capabilities, ownership/heartbeat uptime, coredump info/data, firmware update start/chunk/finish handshakes, QSFP read responses, TSENE sensor responses, firmware logs, and TLV parser self-test echo responses.

## Control Flow

Mailbox initialization clears capability state, initializes the Tx lock, resets both descriptor rings, configures firmware interrupt auto-clear behavior, and clears stale mailbox causes. `fbnic_mbx_poll_tx_ready()` repeatedly resets the Tx ring until firmware signals an interrupt event, enables DMA read/write attributes for Tx/Rx rings, preallocates Rx pages, sends `HOST_CAP_REQ`, and polls until the parsed firmware capability response sets a management version at or above `MIN_FW_VER_CODE`.

Tx messages are allocated as TLV pages, optionally reserve a completion slot under `fw_tx_lock`, DMA-map into the Tx mailbox ring, and publish descriptors by writing upper then lower halves. Tx polling frees messages whose descriptors have firmware-complete set. Rx polling syncs DMA pages for CPU, validates descriptor length, parses TLVs, logs parse failures with a hex dump, then recycles the same page to the Rx tail.

Completion slots are keyed by expected message type and protected by `fw_tx_lock`. Parsers find completions with `fbnic_fw_get_cmpl_by_type()`, fill result-specific union fields, complete waiters, and drop krefs. `fbnic_mbx_flush_tx()` disables new Tx, evicts all outstanding completions with `-EPIPE`, and waits for already-published Tx descriptors to be consumed.

Heartbeat control uses ownership and heartbeat responses to update `last_heartbeat_response`, `firmware_time`, and `prev_firmware_time`. `fbnic_fw_check_heartbeat()` periodically detects missing responses or firmware uptime rollback, disables heartbeat reporting after a fault, and sends another heartbeat request.

## State And Persistence

State lives in `struct fbnic_dev`: `mbx[]` readiness/head/tail/buffer info, `fw_tx_lock`, `cmpl_data[]`, `fw_cap`, heartbeat jiffies, firmware uptime fields, and `fw_heartbeat_enabled`. Firmware capability parsing populates running/stored version/commit data, BMC presence/MAC addresses/allmulti flags, link speed/FEC, active slot, anti-rollback version, and BMC reinit flags. Runtime mailbox state is not persistent across reset; `fbnic_mbx_clean()` unmaps/frees DMA pages and rings are rebuilt.

## Dependencies And Integration Points

The file depends on DMA mapping, bitfield helpers, completions/krefs, delays, `fbnic_tlv` builders/parsers, CSR mailbox and PUL registers, firmware log storage, MAC/RPC TCAM state, and interrupt code that calls `fbnic_mbx_poll()`. Devlink uses coredump and firmware upgrade transmitters. Ethtool uses mailbox self-test and QSFP reads. HWMON/MAC sensor paths use TSENE reads through MAC helpers. RX mode synchronization can send RPC MAC sync messages to firmware.

## Risks And Edge Cases

Mailbox descriptor ordering is delicate: upper/lower write order differs for publish versus invalidate so firmware can detect stable descriptors. Ring-full detection leaves one unused slot; changing the ring length requires preserving power-of-two assumptions in modulo logic. Completion slots are limited (`FBNIC_MBX_CMPL_SLOTS`), so concurrent operations can return `-EXFULL` or `-EEXIST`. The capability parser disables the Tx mailbox if firmware is too old. Log parsing rejects `length >= FBNIC_FW_MAX_LOG_HISTORY`, so firmware's length convention is important. Firmware coredump and update parsers validate offsets and lengths to avoid buffer corruption. `fbnic_fw_mbx_self_test()` does not initialize its enum to success explicitly before waits; success depends on parser setting `cmpl->result` to zero and the local variable not being used on the success path except after conditions.

## Test Signals

Useful tests include mailbox ready polling on probe, capability parsing with old and current firmware, ownership take/release, heartbeat timeout and uptime rollback reporting, TLV self-test, firmware log enable/disable and historical log gating, coredump info/read multi-chunk validation, PLDM update chunk sequencing, QSFP/TSENE read success and mismatched response failures, completion slot exhaustion, mailbox flush during teardown, and DMA mapping failure injection. No executable tests were run for this research item.
