# sources/distributed-fs/ceph-client/drivers/bluetooth/btrsi.c

## Purpose
Provides the Bluetooth HCI adapter glue for Redpine/RSI 91x coexistence devices. It registers an HCI device for the RSI core, forwards outgoing HCI packets into the RSI coexistence queue with required headroom/alignment, receives RSI-framed Bluetooth packets from the core, and exports `rsi_bt_ops` for attach/detach/receive integration.

## Important APIs, Types, And Functions
- `struct rsi_hci_adapter` stores the RSI private pointer, protocol operations, and HCI device.
- `rsi_hci_attach` allocates adapter/HCI state, stores BT context in the RSI core, selects HCI bus based on host interface, installs HCI callbacks, and registers the HCI device.
- `rsi_hci_detach` unregisters/frees the HCI device and adapter.
- `rsi_hci_send_pkt` updates TX stats, ensures `RSI_HEADROOM_FOR_BT_HAL` and 8-byte DMA alignment, then calls `coex_send_pkt(..., RSI_BT_Q)`.
- `rsi_hci_recv_pkt` extracts packet length/type from the RSI frame descriptor, copies the HCI payload into a new skb, and passes it to `hci_recv_frame`.
- `rsi_bt_ops` exports the module operations consumed by the RSI wireless core.

## Control Flow
The RSI core calls `attach` with its private context and operations. This driver allocates and registers an HCI device but leaves open/close/flush as no-ops because the parent core owns hardware power and transport. Bluetooth core TX invokes `send`, which may reallocate headroom and align data before handing the skb to the coexistence queue. Parent RX invokes `recv_pkt`; the driver reads the frame descriptor length, copies bytes after the 16-byte descriptor, sets packet type from descriptor byte 14, and submits the HCI frame upward. Detach tears down HCI registration and frees adapter memory.

## State And Persistence
Persistent state is only `rsi_hci_adapter` for the attachment lifetime. The parent RSI core stores the BT context and owns lower-level hardware state. SKBs are transient; TX ownership transfers to `coex_send_pkt` on success, while RX allocates a fresh skb per frame.

## Dependencies And Integration Points
Depends on Bluetooth HCI core, unaligned helpers, and `net/rsi_91x.h` for `rsi_proto_ops`, `rsi_mod_ops`, host-interface constants, and queue IDs. It integrates as an exported module API rather than as a bus driver with device IDs.

## Risks And Edge Cases
If `skb_realloc_headroom` succeeds but the subsequent DMA alignment adjustment is wrong, payload bytes can be corrupted before the parent sends them. When `skb_headroom` is already sufficient, the function does not enforce DMA alignment. `rsi_hci_recv_pkt` trusts the descriptor length and type without validating the provided buffer size. `rsi_hci_attach` returns `-EINVAL` for all post-allocation failures, losing the original error code.

## Test Signals
Attach/detach over SDIO and USB host interfaces, TX with insufficient and sufficient headroom, misaligned TX buffers, command/ACL/SCO stat updates, parent `coex_send_pkt` failures and ownership behavior, RX frame descriptor length/type parsing, allocation failure paths, and repeated attach/detach without leaked HCI devices or adapter contexts.
