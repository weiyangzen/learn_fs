# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/event.h

## Purpose
`event.h` documents the dual-mailbox firmware event mechanism and declares event IDs, wait-event identifiers, firmware logger metadata, and event handling functions.

## Important APIs and types
It defines RSSI/SNR trigger bit IDs, `EVENT_MBOX_ALL_EVENT_ID`, `enum wlcore_wait_event` values for role stop, peer removal, and DFS config completion, power-save entry result constants, `NUM_OF_RSSI_SNR_TRIGGERS`, and packed `struct fw_logger_information` containing ring-buffer size and read/write pointers.

## Control flow and integration
Firmware fills one of two event buffers while the host processes the other. `wl1271_event_handle()` consumes one mailbox and ACKs it. Command code uses `wlcore_wait_event` names through `wl->ops->wait_for_event()` when synchronous command flows need firmware completion events.

## State and persistence behavior
The header defines no host state directly, but the firmware logger structure maps persistent device memory for logger ring-buffer accounting. Event masks and mailbox buffers are maintained in `struct wl1271`.

## Dependencies and risks
It depends on bit definitions and packed endian fields. Risks include mismatch between chip-specific event decoding and common exported handler prototypes, and wait-event enum changes that break command paths expecting specific completions.

## Test signals
Mailbox event handling, wait-event completion for role stop/peer removal/DFS config, firmware logger pointer parsing, and RSSI trigger delivery validate this interface.
