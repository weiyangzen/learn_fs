# sources/distributed-fs/ceph-client/net/bluetooth/hci_drv.c

## Purpose

`hci_drv.c` implements a small driver-specific HCI pseudo-packet command layer. It lets code send `HCI_DRV_PKT` commands through the regular HCI send path and dispatch them to driver-provided common or driver-specific handlers, then lets handlers report command status or command completion back into the normal receive path as `HCI_DRV_PKT` events. This provides an internal command/event mechanism parallel to controller HCI commands without sending those packets to the physical controller.

## Important APIs, Types, and Functions

`hci_drv_cmd_status()` allocates an skb containing `struct hci_drv_ev_hdr` plus `struct hci_drv_ev_cmd_status`, fills the event opcode `HCI_DRV_EV_CMD_STATUS`, embeds the original command opcode and status byte, marks the skb as `HCI_DRV_PKT`, and injects it with `hci_recv_frame()`.

`hci_drv_cmd_complete()` similarly allocates an event skb for `HCI_DRV_EV_CMD_COMPLETE`, includes the original opcode, status, and optional return parameters, marks the packet type, and injects it through `hci_recv_frame()`.

`hci_drv_process_cmd()` is the dispatcher called by `hci_core.c` from `hci_send_frame()` when an outgoing skb has packet type `HCI_DRV_PKT`. It parses `struct hci_drv_cmd_hdr`, validates that the embedded length equals the remaining skb length, decodes OGF/OCF, selects a handler table from `hdev->hci_drv`, verifies handler existence and exact payload length, and invokes `handler->func(hdev, skb->data, len)`.

## Control Flow

Outgoing driver packets are intercepted before `hdev->send()` so they never reach the transport. `hci_drv_process_cmd()` first rejects malformed short headers or mismatched lengths with `-EILSEQ`. If the device has no `hci_drv` table, if the opcode does not map to an installed handler, or if the handler function is missing, it injects an unknown-command status event. If the payload length differs from `handler->data_len`, it injects an invalid-parameters status event. Only validated commands call the handler.

Handlers are responsible for their own semantics and may use `hci_drv_cmd_status()` or `hci_drv_cmd_complete()` to emit responses. Those responses enter the normal RX queue through `hci_recv_frame()`, preserving monitor/socket visibility and ordering semantics of other received packets.

## State and Persistence Behavior

This file stores no persistent state. It reads `hdev->hci_drv`, handler counts, and handler arrays from the device. Allocated response skbs are transient and owned by the receive path after successful injection. Command payload bytes are consumed directly from the outgoing skb after the header is pulled; the skb is freed by the caller in `hci_send_frame()` after dispatch returns.

## Dependencies and Integration Points

The file depends on `hci_drv.h` for packet header, event, status, and handler definitions; on `hci_core.h` for `struct hci_dev` and `hci_recv_frame()`; on Bluetooth skb helpers for packet typing; and on HCI opcode helpers for OGF/OCF decoding. Its primary integration point is `hci_core.c:hci_send_frame()`, which detects `HCI_DRV_PKT`, calls `hci_drv_process_cmd()`, frees the outgoing skb, and returns the handler result.

## Risks and Edge Cases

The dispatcher deliberately requires exact payload length, which protects handlers from short or overlong payloads but means handler metadata must stay synchronized with command definitions. Handler table indexing is split between common opcodes and `HCI_DRV_OGF_DRIVER_SPECIFIC` OCFs; incorrect OGF/OCF assignment will produce unknown-command events. Response allocation failures return `-ENOMEM` and no event is injected, so callers waiting for a response need timeout behavior. Because responses re-enter `hci_recv_frame()`, they require the device to be up or initializing just like other received frames.

## Test Signals

Tests should cover malformed command headers, length mismatch, missing `hci_drv`, unknown common opcode, unknown driver-specific OCF, invalid handler payload length, successful handler dispatch, command status response injection, command complete response with return parameters, and behavior when the HCI device is not up. Runtime signals include `HCI_DRV_PKT` monitor traces, handler return codes, injected command-status/complete events, and command timeout behavior if a handler fails to respond.
