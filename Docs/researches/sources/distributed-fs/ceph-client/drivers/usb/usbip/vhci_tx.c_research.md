# sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_tx.c

## Purpose

`vhci_tx.c` sends local USB core requests from the virtual host controller to the remote USB/IP server. It serializes pending URBs into CMD_SUBMIT PDUs and local unlink requests into CMD_UNLINK PDUs.

## Important APIs, Types, and Functions

`setup_cmd_submit_pdu()` fills command, sequence, remote device ID, direction, endpoint, submit fields, and setup packet. `dequeue_from_priv_tx()` moves pending submits from `priv_tx` to `priv_rx` before send. `vhci_send_cmd_submit()` builds kvec arrays for headers, OUT payloads, SG payloads, and isochronous descriptors, then sends them with `kernel_sendmsg()`. `dequeue_from_unlink_tx()` moves pending unlink requests to `unlink_rx`. `vhci_send_cmd_unlink()` sends command headers for unlink target sequences. `vhci_tx_loop()` drains both queues and sleeps on `waitq_tx`.

## Control Flow

HCD enqueue adds `vhci_priv` to `priv_tx`; the TX loop moves it to `priv_rx` so RX can match the return. OUT transfers include payload; IN transfers send only command metadata. Isochronous URBs also send packed iso descriptors. Local dequeues add `vhci_unlink` to `unlink_tx`; TX moves it to `unlink_rx` before sending so RX can match RET_UNLINK.

## State and Persistence Behavior

The file advances transient list state from transmit-pending to receive-pending. It sets `URB_DMA_MAP_SG` for SG URBs before packing to the USB/IP UAPI flag space. No persistent state exists.

## Dependencies and Integration Points

It depends on common PDU packing/endian helpers, socket sendmsg, scatterlist iteration, VHCI list conventions, HCD enqueue/dequeue paths, and the common event handler for send failures.

## Risks and Test Signals

Risks include partial sends, SG lengths not matching transfer length, isochronous descriptor allocation failure, using wrong side event constants on allocation failure, and leaving items in receive-pending after send failure. Test signals include bulk/control/iso submit, SG OUT submit, unlink submit, send failure cleanup, and RX matching of moved list entries.
