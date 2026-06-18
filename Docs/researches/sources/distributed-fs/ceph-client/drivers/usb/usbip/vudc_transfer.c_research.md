# sources/distributed-fs/ceph-client/drivers/usb/usbip/vudc_transfer.c

Purpose: emulates USB bus transfer progress between host-side USBIP URBs and gadget-driver `usb_request`s. A timer processes queued URBs, handles standard control requests, copies payloads, and queues USBIP return packets.

Important APIs/types/functions: `get_frame_limit()` estimates per-frame bandwidth by USB speed. `handle_control_request()` handles standard SET_ADDRESS, SET/CLEAR_FEATURE, and GET_STATUS locally. `transfer()` copies data between URB and gadget request queues, handles short packets, zero packets, overflow status, and gives completed gadget requests back. `v_timer()` is the scheduler over `udc->urb_queue`. `v_init_timer()`, `v_start_timer()`, `v_kick_timer()`, and `v_stop_timer()` manage `transfer_timer` state.

Control flow: RX enqueues URBs and kicks the timer. `v_timer()` computes current frame budget, clears endpoint `already_seen`, scans queued URBs, handles unlink/halt/setup cases, calls gadget `setup()` for unhandled control requests, transfers data for bulk/control/interrupt endpoints, rejects isochronous with `-EXDEV`, and moves completed URBs to the TX queue. If URBs remain, it re-arms for the next frame; otherwise it transitions idle.

State and persistence: mutable state includes `udc->urb_queue`, endpoint flags (`halted`, `wedged`, `setup_stage`, `already_seen`), device status bits, address, URB statuses/actual lengths, request statuses/actual lengths, and timer state (`STOPPED`, `IDLE`, `RUNNING`). All timer processing occurs under `udc->lock`, with temporary unlocks around gadget callbacks/giveback.

Dependencies and integration: bridges `vudc_rx.c` queued URBs, gadget endpoint request queues, Linux USB gadget callbacks, and `vudc_tx.c` return queue helpers. Uses kernel timers and USB descriptor/status constants.

Risks: timer accuracy and bandwidth accounting are approximate. Unlocking around gadget callbacks requires careful rescan logic because request queues may change. Isochronous endpoints are accepted by RX but completed with `-EXDEV`. Standard control emulation is incomplete, so gadget setup fallback is critical.

Test signals: control enumeration requests, endpoint halt/clear halt, bulk IN/OUT short and exact packets, zero-length packet behavior, request overflow/underflow, unlink while active, no-speed idle behavior, and timer re-arm when queues remain.
