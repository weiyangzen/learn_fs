# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb-v2/usb_urb.c

Purpose: generic dvb-usbv2 streaming URB helper for bulk and isochronous USB data paths. It allocates stream buffers, allocates/fills URBs, submits/kills/reconfigures them, dispatches completed payloads to the stream callback, and frees resources.

Important APIs/types/functions: public functions are `usb_urb_initv2()`, `usb_urb_submitv2()`, `usb_urb_killv2()`, `usb_urb_reconfig()`, and `usb_urb_exitv2()`. Internal helpers allocate/free URBs and buffers for bulk/isoc configurations. `usb_urb_complete()` is the shared completion handler that handles status codes, iterates isoc frame descriptors, invokes `stream->complete()`, clears isoc frame metadata, and resubmits the URB.

Control flow: dvb-usbv2 stream setup calls `usb_urb_initv2()` with static or runtime stream properties. Starting a stream calls submit, optionally reconfiguring the URBs if a frontend-specific stream config is provided. Completion callbacks pass valid data chunks upstream and immediately resubmit unless the URB was killed or shut down. Stop kills all submitted URBs, and exit frees URBs and buffers.

State and persistence: mutable state lives in `struct usb_data_stream`: copied `props`, `urb_list`, `buf_list`, `buf_num`, `buf_size`, `urbs_initialized`, `urbs_submitted`, state flags, device pointer, and completion callback. Buffers persist for the life of the stream and can be reused by reconfigured URBs when large enough.

Dependencies and integration: depends on Linux USB URB APIs and `dvb_usb_common.h` stream structures. It is shared by dvb-usbv2 bridge drivers that request bulk or isoc streams and by runtime stream configuration hooks such as MxL111SF and LME2510.

Risks: allocation uses `GFP_ATOMIC` in initialization paths where sleeping allocation might be more resilient. `usb_urb_reconfig()` checks bulk buffer size using `stream->props.u.bulk.buffersize` rather than the new `props->u.bulk.buffersize`, so growing a bulk buffer request can be incorrectly accepted if old props are smaller or stale. Completion always resubmits and ignores submit errors. Isoc frame errors are logged but do not affect stream health. No DMA mapping is used despite debug printing `dma_addr`.

Test signals: bulk and isoc stream init/submit/kill/exit under dvb-usbv2; runtime reconfiguration between endpoints/frame sizes; forced URB error statuses; disconnect while URBs are active; kmemleak/resource checks for buffers and URBs; data callback count and byte accounting for bulk and isoc frames.
