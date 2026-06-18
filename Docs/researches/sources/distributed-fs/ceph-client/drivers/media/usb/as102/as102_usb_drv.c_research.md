# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_usb_drv.c

## Purpose
Implements USB probing, disconnect, character-device registration, command transport, firmware packet transfer, and DVB transport-stream URB streaming for AS102 devices.

## Important APIs, types, and functions
`as102_usb_id_table` maps vendor/product IDs to device names and eLNA configs. `as102_usb_driver` is the USB driver exported to `as102_drv.c`. `as102_usb_xfer_cmd()` sends and receives vendor control messages `0xf1`/`0xf2` using `cmd_xid`. `as102_send_ep1()` uploads firmware packets over bulk endpoint 1. `as102_read_ep2()` reads endpoint 2 synchronously. `as102_alloc_usb_stream_buffer()` allocates one coherent buffer spanning `MAX_STREAM_URB * AS102_USB_BUF_SIZE` and assigns slices to URBs. `as102_urb_stream_irq()` feeds received bytes to `dvb_dmx_swfilter()` and resubmits while `streaming` is nonzero. Probe allocates `as102_dev_t`, registers `/dev/aton2-*`, allocates stream buffers, and calls `as102_dvb_register()`.

## Control flow and state
USB probe establishes device identity, bus ops, command token pointers, kref, and USB ref. DVB feed start later submits all stream URBs; each URB completion pushes TS bytes to demux and self-resubmits. Disconnect unregisters DVB, frees stream buffers, deregisters the USB class device, clears interface data, and drops the kref.

## Dependencies and integration points
Integrates with Linux USB core, DVB demux, firmware upload, and AS102 private operations. Also exposes a simple character device open/release path that pins `as102_dev_t` via kref.

## Risks and test signals
Risks include short USB transfers returning `-1` instead of a standard errno, resubmission depending on the shared `streaming` counter, coherent buffer pointer arithmetic on `void *`, and disconnect while character device references remain. Test signals include device-node creation, successful firmware upload over EP1, command request/response over control endpoint, sustained endpoint 2 streaming, and clean disconnect during active feeds.
