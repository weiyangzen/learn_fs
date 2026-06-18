<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/j721e-csi2rx/j721e-csi2rx.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/j721e-csi2rx/j721e-csi2rx.c

## Purpose

This is the TI J721E CSI2RX shim wrapper V4L2 capture driver. It bridges a Cadence CSI2RX subdevice to a video capture node, configures the TI shim registers, negotiates pixels-per-clock, receives frames through a DMA engine channel, and exposes a media-controller V4L2 capture interface.

## Important APIs, types, and functions

- `ti_csi2rx_formats[]` maps V4L2 fourcc formats to media-bus codes, MIPI CSI-2 data types, bits per pixel, and shim unpacking sizes.
- `ti_csi2rx_*_fmt*()` ioctl helpers enumerate, clamp, get, try, and set capture formats and frame sizes.
- `ti_csi2rx_notifier_register()`, `csi_async_notifier_bound()`, and `csi_async_notifier_complete()` bind the `csi-bridge` child subdevice, register the video node, create the immutable media link, and register subdev nodes.
- `ti_csi2rx_setup_shim()` programs pixel reset, CSI datatype, YUV422 byte order, multi-pixel mode, and PSI-L tags.
- `ti_csi2rx_start_dma()`, `ti_csi2rx_dma_callback()`, `ti_csi2rx_stop_dma()`, and `ti_csi2rx_drain_dma()` manage DMA transactions and stale endpoint draining.
- `ti_csi2rx_start_streaming()` and `ti_csi2rx_stop_streaming()` coordinate the media pipeline, shim, DMA, and upstream subdevice stream state.

## Control flow

Probe allocates `struct ti_csi2rx_dev`, maps the shim registers, initializes a DMA channel named `rx0` and a coherent drain buffer, initializes media/V4L2/video state with a default UYVY 640x480 capture format, initializes vb2, registers an async notifier for the `csi-bridge` fwnode, and populates child platform devices. Notifier completion registers the video device and creates an immutable enabled link from bridge source pad 1 to the video sink pad.

Userspace configures formats through the video node. Width is rounded down to the number of pixels per 16-byte PSI-L word and clamped to arbitrary 16K limits; interlaced formats are forced to `V4L2_FIELD_NONE`. Link validation compares source pad width, height, field, media-bus code, and fourcc before streaming.

Stream-on requires queued buffers, starts the media pipeline, configures shim registers, resets sequence, starts DMA for the first queued buffer, marks DMA active, and calls upstream `s_stream(1)`. DMA callbacks timestamp and complete buffers, then submit all queued buffers. If DMA goes idle due to no buffers, `buffer_queue()` drains stale data and restarts DMA when a new buffer arrives. Stop disables pipeline and shim, stops upstream streaming, drains/terminates DMA, and returns all queued/submitted buffers as errors.

## State and persistence behavior

`struct ti_csi2rx_dev` stores the device, shim base, V4L2/media/video objects, async notifier, source subdevice, vb2 queue, mutex, current format, DMA state, sequence counter, and negotiated pixels-per-clock. DMA state tracks queued buffers, submitted buffers, state enum, DMA channel, and a persistent coherent drain buffer for the lifetime of the driver. No disk persistence exists.

## Dependencies and integration points

It depends on platform OF matching (`ti,j721e-csi2rx-shim`), DMA engine, Cadence CSI2RX media helper `cdns_csi2rx_negotiate_ppc()`, MIPI CSI-2 datatypes, V4L2/media-controller APIs, videobuf2 DMA-contig, fwnode async registration, and child platform population for the bridge device.

## Risks and edge cases

DMA draining is used to avoid stale PSI-L data after frame drops or stopping one stream in multi-stream cases; drain timeout is tolerated but other drain errors warn that the next frame may be bad. The DMA callback submits every queued buffer while holding the DMA lock, so start-DMA failures must mark individual buffers with error. The shim size calculation changes for multiple pixels per clock and packed YUV; wrong negotiation or format metadata would corrupt packing. Remove unregisters the video device unconditionally, so notifier-completion failures must keep lifecycle ordering correct.

## Test signals

Validate media graph creation with a Cadence bridge child, format enumeration with and without `mbus_code`, link validation failures, MMAP/DMABUF streaming, no-buffer underrun followed by restart, drain timeout behavior, multiple pixel-per-clock negotiation, all supported Bayer/YUV/RGB formats, and repeated probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/j721e-csi2rx/j721e-csi2rx.c -->
