# sources/distributed-fs/ceph-client/drivers/usb/gadget/u_f.c

Purpose: shared USB gadget function utility implementing request allocation with endpoint-aware buffer sizing.

Important APIs, types, and functions: `alloc_ep_req(struct usb_ep *ep, size_t len)` allocates a `usb_request` with `usb_ep_alloc_request`, sets `req->length`, allocates `req->buf`, and exports the helper with `EXPORT_SYMBOL_GPL`.

Control flow: the helper allocates the request in atomic context. For OUT endpoints, it aligns requested length with `usb_ep_align(ep, len)` to satisfy controller DMA/cache constraints; for IN endpoints it keeps the requested length. If buffer allocation fails, it frees the request and returns NULL.

State and persistence: no persistent state. The caller owns the returned request and buffer and must free both through the matching endpoint/function cleanup path.

Dependencies and integration points: depends on USB endpoint descriptors, `linux/usb/func_utils.h`, and endpoint allocator/free APIs. Function drivers use it to standardize request and buffer allocation.

Risks: callers must only pass endpoints with valid descriptors because direction is read from `ep->desc`. GFP_ATOMIC can fail under memory pressure. The helper allocates but does not initialize completion callbacks or list nodes.

Test signals: call from IN and OUT endpoints and verify lengths, alignment, NULL handling on allocation failure, and correct cleanup through `usb_ep_free_request` plus `kfree(req->buf)` in callers.
