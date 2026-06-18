# sources/distributed-fs/ceph-client/drivers/usb/usbip/vhci_rx.c

## Purpose

`vhci_rx.c` receives USB/IP responses from the remote host for the virtual host controller. It matches return PDUs to pending local URBs or unlink requests, receives payloads and isochronous descriptors, and gives URBs back to the USB core.

## Important APIs, Types, and Functions

`pickup_urb_and_free_priv()` searches `priv_rx` by sequence, removes the `vhci_priv`, clears `urb->hcpriv`, and returns the URB. `vhci_recv_ret_submit()` unpacks RET_SUBMIT, receives IN payload and iso descriptors, restores iso padding, unlinks the URB from HCD endpoint tracking, and calls `usb_hcd_giveback_urb()`. `vhci_recv_ret_unlink()` matches `unlink_rx`, finds the target submit URB if still pending, applies returned status, and gives it back. `vhci_rx_pdu()` handles socket receive and dispatch.

## Control Flow

`vhci_rx_loop()` runs until stopped or an event bit appears. Each response header is read, endian-corrected, and dispatched. Missing submit sequences or unknown commands are treated as TCP/protocol errors. Idle `-EAGAIN` is ignored only when no submitted URBs are awaiting replies.

## State and Persistence Behavior

The file consumes runtime `priv_rx` and `unlink_rx` entries created by VHCI TX/dequeue paths. It mutates URB status/length fields from remote responses and has no persistent state.

## Dependencies and Integration Points

It depends on USB/IP common receive/pack helpers, VHCI HCD endpoint unlinking, USB core giveback rules, kthreads, KCOV remote coverage hooks, and the common event handler.

## Risks and Test Signals

Risks include malicious response sequence numbers, remote lengths larger than URB buffers, iso descriptor corruption, giving back URBs after local unlink races, and treating transport EOF/timeouts correctly. Test signals include normal RET_SUBMIT, RET_UNLINK before and after submit return, invalid command handling, IN payload receive, isochronous receive/padding, SG flag cleanup, and TCP reset/down events.
