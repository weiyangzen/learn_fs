# sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_tx.c

## Purpose

`stub_tx.c` is the host-side transmit path. It converts completed physical URBs and unlink outcomes into USB/IP return PDUs and sends them to the remote VHCI client.

## Important APIs, Types, and Functions

`stub_complete()` is the USB completion callback. It records final status, waits for all split SG URBs when needed, converts unlinking requests into unlink replies, or moves normal completions to `priv_tx`. `setup_ret_submit_pdu()` and `setup_ret_unlink_pdu()` build return headers. `stub_send_ret_submit()` sends RET_SUBMIT headers, IN payload data, packed isochronous descriptors, and reassembled split-SG data. `stub_send_ret_unlink()` sends RET_UNLINK headers. `stub_tx_loop()` drains submit replies before unlink replies and waits on `tx_waitq`.

## Control Flow

Completions enqueue work under `priv_lock` and wake the TX thread. The TX loop drains all normal completions, freeing `priv_free` entries after successful send, then drains unlink completions. Send failures queue TCP error events. The ordering intentionally lets late unlink requests see the already completed submit result before the unlink reply.

## State and Persistence Behavior

The file moves `stub_priv` through `priv_tx` and `priv_free`, and `stub_unlink` through `unlink_tx` and `unlink_free`. State is transient per connection.

## Dependencies and Integration Points

It depends on kernel sockets, common PDU packing/endian helpers, isochronous descriptor packing, scatterlist iteration, stub RX list conventions, and USB completion context rules.

## Risks and Test Signals

Risks include partial `kernel_sendmsg()` writes, inconsistent isochronous actual-length sums, freeing URB state while a connection closes, split-SG status aggregation, and allocating `kvec` arrays in response to hostile URBs. Test signals include IN/OUT completions, isochronous IN returns, split-SG reassembly, unlink races, TCP send failure, and cleanup after device removal.
