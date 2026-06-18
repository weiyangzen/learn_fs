# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_rx.c

Purpose: receive-side USB/IP protocol handling for vudc. It reads TCP PDUs, converts `USBIP_CMD_SUBMIT` into kernel URBs queued on the emulated gadget endpoints, and handles `USBIP_CMD_UNLINK` cancellation requests.

Important APIs/types/functions: `alloc_urb_from_cmd()` allocates `struct urb`, copies USBIP submit fields via `usbip_pack_pdu()`, allocates transfer/setup buffers, and sets a minimal pipe direction/type. `v_recv_cmd_submit()` allocates `struct urbp`, finds the target `vep`, validates isochronous packet counts, receives OUT/ISO payloads with `usbip_recv_xbuff()` and `usbip_recv_iso()`, then queues the URB. `v_recv_cmd_unlink()` marks matching queued URBs with `-ECONNRESET` or queues an immediate RET_UNLINK. `v_rx_pdu()` reads/corrects a `usbip_header`, checks `SDEV_ST_USED`, and dispatches. `v_rx_loop()` is the kthread body.

Control flow: the RX thread loops until stop or USBIP event. Each PDU is read in full, endian-corrected, and rejected if the USBIP device is not in use. SUBMIT resolves endpoint, allocates URB state, receives payload descriptors, kicks the transfer timer, and appends to `udc->urb_queue`. UNLINK scans the same queue under `udc->lock`; found URBs are completed later by the timer, while missing URBs generate an unlink response immediately on `tx_queue`.

State and persistence: `urbp` stores endpoint, type, `seqnum`, and `new` setup-stage flag. Queue state is protected by `udc->lock`; transmit queue insertion additionally uses `lock_tx`. Protocol errors add `VUDC_EVENT_ERROR_TCP`; allocation failures add `VUDC_EVENT_ERROR_MALLOC`.

Dependencies and integration: relies on `usbip_common` PDU helpers, vudc endpoint lookup, transfer timer (`v_kick_timer()`), and TX queue helpers (`v_enqueue_ret_unlink()`). It feeds `vudc_transfer.c`, which consumes `urb_queue`.

Risks: pipe setup is intentionally minimal and marked FIXME, so assumptions in shared usbip helpers matter. Isochronous support is partially validated here but later rejected in the timer path. Endpoint lookup occurs under lock, but endpoint state can still change before transfer, so transfer-side checks remain important.

Test signals: submit to valid/invalid endpoints, OUT payload reception, IN zero-payload submit, unlink before and after completion, malformed/truncated TCP header, non-`SDEV_ST_USED` socket state, and isochronous packet count bounds.
