# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/wmi.h

## Purpose
`wmi.h` declares the ath9k_htc WMI protocol structures, command/event IDs, driver-side WMI state, and helper macros for issuing common commands. It is the contract between host driver code and target firmware for the HTC WMI control service.

## Important APIs, types, and constants
Protocol structs include `wmi_cmd_hdr`, `wmi_fw_version`, `wmi_event_swba`, `wmi_event_txstatus`, `register_write`, and `register_rmw`. Command IDs cover firmware version, interrupts, init, TX/RX control, VAP/node operations, register read/write/RMW, rate-control updates, stats, and bitrate masks. Event IDs cover target-ready, SWBA, fatal, timeout/beacon miss/delba, and TX status. `struct wmi` stores HTC endpoint state, locks, completion, sequence counters, event queue/tasklet, pending TX events, stopped flag, and multi-write/RMW batching buffers.

## Control flow and integration
The header provides declarations implemented in `wmi.c` and two command macros, `WMI_CMD` and `WMI_CMD_BUF`, that call `ath9k_wmi_cmd()` with a conventional response buffer and two-second timeout. Other ath9k_htc code includes this header to send firmware commands and interpret WMI events.

## State and persistence behavior
`struct wmi` is long-lived per USB device. It persists command sequencing, queued events, locks, and batching arrays across individual commands. The multi-write and multi-RMW counters/indexes support batching multiple register operations before sending to firmware.

## Dependencies
The file depends on ath9k_htc private types, HTC endpoint IDs, Linux SKBs/list/spinlock/mutex/completion primitives, and firmware command payload layout. Endianness annotations are part of the wire contract.

## Risks
Risks include host/firmware ABI drift, packed-structure size changes, wrong endian conversion, overflow of `MAX_CMD_NUMBER` or `MAX_RMW_CMD_NUMBER` batching arrays, and assuming event payload lengths without validating received SKB lengths in consumers.

## Test signals
Signals include build-time structure compatibility, firmware command smoke tests, multi-register read/write/RMW tests, TX status parsing, event dispatch coverage, and timeout/unplug handling with no use-after-free of `struct wmi`.
