# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_tx.c

Purpose: transmit-side USB/IP response path for vudc. It sends `USBIP_RET_SUBMIT` completions and `USBIP_RET_UNLINK` replies over the attached TCP socket.

Important APIs/types/functions: `setup_base_pdu()`, `setup_ret_submit_pdu()`, and `setup_ret_unlink_pdu()` build response headers. `v_send_ret_submit()` constructs iovecs for header, IN data, and optional ISO descriptors, sends them with `kernel_sendmsg()`, and frees the completed URB package. `v_send_ret_unlink()` sends unlink status and frees the unlink record. `v_send_ret()` drains `udc->tx_queue`. `v_tx_loop()` waits on `tx_waitq`. `v_enqueue_ret_submit()` and `v_enqueue_ret_unlink()` allocate `tx_item`s under spinlocks.

Control flow: transfer/unlink code appends TX items and wakes `tx_waitq`. The TX thread drains all available items under `lock_tx`, releasing the lock while sending each item. Send size mismatches add a TCP error event. Submit completions include IN payload only when appropriate; ISO IN payload is sent per frame descriptor plus an ISO descriptor PDU.

State and persistence: `tx_queue` holds `TX_SUBMIT` and `TX_UNLINK` items. Ownership transfers to TX send functions, which free URB/unlink memory after send attempt. No persistent storage exists.

Dependencies and integration: consumes outputs from `vudc_transfer.c` and `vudc_rx.c`, uses usbip endian/packing helpers, socket `kernel_sendmsg()`, and USBIP event flags. Kthread lifecycle is created from sysfs attach.

Risks: allocation failures in enqueue use `GFP_ATOMIC`; the code reports `VDEV_EVENT_ERROR_MALLOC`, which should be checked against the surrounding event enum naming. A failed submit send still frees the URB package, so recovery is connection-level. ISO handling is mostly passthrough despite transfer-side lack of true ISO support.

Test signals: RET_SUBMIT for IN and OUT, RET_UNLINK success and cancellation status, short socket writes, queue wakeups, empty queue wait behavior, and memory ownership under send failure.
