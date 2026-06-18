# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/usb.h

## Purpose
`usb.h` defines the private USB bus contract used by `usb.c`: endpoint constants, control request IDs, diagnostic message formats, logical pipe IDs, pipe/device state containers, URB context state, and the helper that retrieves USB-private data from `struct ath10k`.

## Important APIs, Types, and Functions
Constants define 32 TX and 32 RX URB contexts per mapped pipe and a 4096-byte RX buffer. Endpoint address macros map firmware application endpoints to logical pipe IDs: control/data/data2/interrupt IN endpoints and control/low/medium/high data OUT endpoints. Vendor control request IDs cover BMI send/receive and diagnostic command/response transactions. Packed structures `ath10k_usb_ctrl_diag_cmd_write`, `ath10k_usb_ctrl_diag_cmd_read`, and `ath10k_usb_ctrl_diag_resp_read` define the little-endian USB diagnostic protocol. `enum ath10k_usb_pipe_id` defines the logical pipe namespace, and `ath10k_usb_priv()` casts `ar->drv_priv` to `struct ath10k_usb`.

## Control Flow, State, and Persistence
`struct ath10k_usb_pipe` persists all per-endpoint runtime state: free URB context list, submitted URB anchor, total and available URB counts, repost threshold, USB pipe handle, endpoint address, logical pipe number, max packet size, TX flag, completion work, skb completion queue, and endpoint descriptor pointer. `struct ath10k_usb` persists global USB state: the spinlock protecting pipe free lists and counts, Linux USB device/interface, all pipes, diagnostic buffers, and the owning `ath10k` pointer. `struct ath10k_urb_context` binds a submitted or free URB context to its pipe and current skb.

## Dependencies and Integration Points
The header relies on Linux USB, skb, list, workqueue, and bit macros made available through the including C file and ath10k headers. Its structures are consumed by `usb.c` and are sized as the private tail allocated by `ath10k_core_create()`. Endpoint constants must agree with the USB firmware interface and with `ath10k_usb_get_logical_pipe_num()` in `usb.c`; diagnostic structures must agree with target firmware control-message parsing.

## Risks and Test Signals
Risks are mostly ABI and state-layout risks. Endpoint address changes, diagnostic command-size changes, or new chipset pipe layouts require synchronized updates in both the header and pipe setup logic. `ATH10K_USB_PIPE_INVALID` aliases `ATH10K_USB_PIPE_MAX`, so bounds checks must reject it before indexing. The shared `cs_lock` protects only the free list and count, not every pipe field. Test signals include compile coverage for the private structures, descriptor-to-pipe mapping tests, validation of packed diagnostic payload sizes and endianness, and teardown checks that all allocated URB contexts return to the pipe free list.
