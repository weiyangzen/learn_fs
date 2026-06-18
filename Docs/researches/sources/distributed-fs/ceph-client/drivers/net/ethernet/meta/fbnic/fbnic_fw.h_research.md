# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_fw.h

## Purpose

`fbnic_fw.h` declares the firmware mailbox data structures, completion payloads, firmware capability model, mailbox APIs, firmware request APIs, firmware version formatting helpers, QSPI section IDs, heartbeat timing, TLV message IDs, capability attribute IDs, and firmware link-mode/FEC enums. It is the interface between firmware protocol implementation (`fbnic_fw.c`) and users such as devlink, ethtool, IRQ, hwmon, debugfs, MAC/RPC sync, and probe/remove lifecycle code.

## Important APIs, Types, And Functions

`struct fbnic_fw_mbx` stores mailbox readiness, head/tail indices, and per-descriptor TLV page/DMA address info. `struct fbnic_fw_ver` stores a packed version code plus commit string. `struct fbnic_fw_cap` stores running/stored firmware and bootloader versions, stored UNDI version, active slot, BMC MAC addresses, BMC flags, link speed/FEC, and anti-rollback version. `struct fbnic_fw_completion` wraps a completion, kref, result, response message type, and a union of payloads for coredump info/data, firmware update chunk offsets, QSFP EEPROM data, and sensor values.

Public APIs include mailbox lifecycle and polling (`fbnic_mbx_init()`, `fbnic_mbx_clean()`, `fbnic_mbx_set_cmpl()`, `fbnic_mbx_clear_cmpl()`, `fbnic_mbx_poll()`, `fbnic_mbx_poll_tx_ready()`, `fbnic_mbx_flush_tx()`), mailbox self-test, ownership/heartbeat, coredump, firmware upgrade, QSFP, TSENE, log streaming, RPC MAC sync, completion allocation/free, and firmware version string formatting. `fbnic_mbx_wait_for_cmpl()` waits up to `FBNIC_MBX_RX_TO_SEC`.

## Control Flow

The header defines no executable flow beyond the inline completion wait and version-format macros. It shapes flow in callers by pairing each xmit helper with the matching response message ID and completion union member. Message IDs distinguish requests and responses for host capabilities, ownership, heartbeat, coredump, firmware update, QSFP read, TSENE read, firmware logs, and RPC MAC sync.

## State And Persistence

The declared structures are embedded in `struct fbnic_dev` or allocated per mailbox operation. Firmware capability state persists in memory across normal operation and is reset by mailbox init. Completion objects persist until their kref reaches zero; parsers and waiters share them. Constants such as `FBNIC_FW_LOG_MAX_SIZE`, `FBNIC_FW_MAX_LOG_HISTORY`, and commit string sizes constrain runtime buffers and parser behavior.

## Dependencies And Integration Points

The file depends on Linux completions, Ethernet address sizing, integer types, and CSR firmware-version masks. It integrates with `fbnic_fw.c` for implementation, `fbnic_devlink.c` for info/flash/coredump, `fbnic_ethtool.c` for firmware version and EEPROM/self-test, `fbnic_fw_log.c` for log enablement, `fbnic_irq.c` for mailbox IRQ lifecycle, and MAC/RPC/hwmon paths for sensor and MAC synchronization.

## Risks And Edge Cases

Flexible array completion payloads require callers to allocate enough private storage through `__fbnic_fw_alloc_cmpl()`. `FBNIC_FW_CAP_RESP_COMMIT_MAX_SIZE` depends on ethtool firmware version string length and formatted prefix length; longer firmware commit strings are truncated. Message IDs and attribute IDs must stay synchronized with firmware. `fbnic_mbx_wait_for_cmpl()` is a long blocking wait, so callers must use it only where sleeping is allowed. The mailbox buffer model assumes single-page TLV messages and descriptor length limits from CSR definitions.

## Test Signals

Useful checks include compile-time coverage of all declared helpers, firmware version string formatting with and without commit strings, completion allocation sizes for coredump/QSFP payloads, timeout behavior from `fbnic_mbx_wait_for_cmpl()`, and ABI alignment of message/attribute IDs with firmware. No executable tests were run for this research item.
