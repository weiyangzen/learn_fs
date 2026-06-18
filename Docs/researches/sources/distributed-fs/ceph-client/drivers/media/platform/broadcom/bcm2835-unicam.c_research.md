# sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/bcm2835-unicam.c

## Purpose
This driver directly controls the Broadcom BCM283x/BCM271x Unicam CSI-2/CCP2 receiver without VideoCore firmware. It registers a media device, an internal V4L2 bridge subdevice with stream routing, and two capture nodes: one for image data and one for embedded metadata. It receives sensor data and writes it to SDRAM, optionally repacking Bayer formats.

## Important APIs, Types, and Functions
`struct unicam_device` owns MMIO, clocks, media/V4L2 devices, async notifier, sensor endpoint, bridge subdev, bus configuration, pipeline state, and two `struct unicam_node` instances. `struct unicam_node` owns a video device, vb2 queue, DMA queue, current/next buffers, default format, and dummy buffer. Important functions include `unicam_isr()`, `unicam_start_rx()`, `unicam_start_metadata()`, `unicam_disable()`, subdev routing/format/stream ops, `unicam_start_streaming()`, `unicam_stop_streaming()`, `unicam_video_link_validate()`, `unicam_register_node()`, `unicam_async_nf_init()`, and `unicam_probe()`.

## Control Flow
Probe allocates `unicam_device`, maps Unicam and CMI registers, obtains `lp` and `vpu` clocks, requests the IRQ, enables runtime PM, registers the media/V4L2 device, initializes the internal subdev, and registers an async notifier for the remote sensor. When binding completes, it creates immutable links from sensor to bridge and from bridge source pads to the image and metadata video nodes. Starting a video queue starts the media pipeline, records which Unicam nodes are active, validates data lanes, arms the first queued buffer, waits until all required nodes are started, resumes runtime PM, and enables bridge streams. The bridge stream enable programs metadata DMA if needed, configures lanes, packet IDs, interrupts, packing, DMA stride/address, and starts the sensor. IRQ handling clears status, handles frame-end before frame-start, completes current buffers, schedules dummy buffers when user buffers are unavailable, schedules next queued buffers at frame-start/line interrupts, increments sequence, and queues frame-sync events.

## State and Persistence
State is volatile. `kref` protects device lifetime across registered video nodes. `media_pipeline` tracks active graph use. `sequence` and `frame_started` track sensor frame numbering independent of dequeued buffer count. Each node has `cur_frm`, `next_frm`, a spinlock-protected DMA queue, and a coherent dummy buffer. Runtime PM raises the VPU clock minimum to 250 MHz and enables the CSI clock while streaming.

## Dependencies and Integration Points
The driver uses the media controller, V4L2 async/fwnode/subdev stream APIs, vb2 DMA-contig, runtime PM, common clocks, OF graph endpoints, MIPI CSI-2 data types, and the register definitions in `bcm2835-unicam-regs.h`. It accepts CSI-2 D-PHY and CCP2 endpoints and queries sensor mbus config/frame descriptors when available.

## Risks and Edge Cases
Frame-start/frame-end ordering is delicate; the driver handles simultaneous FE/FS to avoid losing buffers. Dummy buffers avoid stopping hardware but mean frames can be dropped when userspace is late. Image capture is required in any active pipeline; metadata-only pipelines fail. Data-lane counts must match sensor and DT limits. Link validation has legacy RGB/BGR compatibility warnings. Runtime clock rate constraints are essential to avoid FIFO overruns and image corruption. The remove path must unregister nodes and async state without dropping references prematurely.

## Test Signals
Use media-ctl to verify immutable links, routes, and subdev nodes. Test CSI-2 1/2/4-lane and CCP2 endpoint parsing, image plus metadata synchronized streaming, late-buffer dummy behavior, frame-sync events, Bayer repacking formats, link-validation failures, runtime PM clock programming, IRQ status under frame start/end/line interrupts, and pipeline start/stop ordering for one or both video nodes.
