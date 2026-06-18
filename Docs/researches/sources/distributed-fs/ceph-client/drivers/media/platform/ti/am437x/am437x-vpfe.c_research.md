# sources/distributed-fs/ceph-client/drivers/media/platform/ti/am437x/am437x-vpfe.c

## Purpose
Implements the TI AM437x VPFE capture driver. It programs the CCDC/image sensor interface, binds one remote camera/decoder subdevice through the firmware graph, exposes a V4L2 video capture node, manages vb2 DMA buffers, and supports standard/input/format/crop configuration plus a private CCDC raw-parameter ioctl.

## Important APIs, Types, And Functions
Important tables are `vpfe_standards` for 525/625-line analog standards and `formats[]` for YUYV/UYVY/YVYU/VYUY Bayer and RGB565 media-bus mappings. CCDC helpers include register accessors, `vpfe_ccdc_restore_defaults()`, `vpfe_ccdc_config_ycbcr()`, `vpfe_ccdc_config_raw()`, `vpfe_ccdc_set_hw_if_params()`, `vpfe_config_ccdc_image_format()`, and `vpfe_config_image_format()`. V4L2 entry points include open/release, querycap, format enum/get/try/set, frame-size enum, input/std ioctls, selection crop get/set, default ioctl `VIDIOC_AM437X_CCDC_CFG`, and vb2 ioctls.

Streaming state is controlled by `vpfe_start_streaming()`, `vpfe_stop_streaming()`, `vpfe_isr()`, `vpfe_schedule_next_buffer()`, `vpfe_handle_interlaced_irq()`, and `vpfe_process_buffer_complete()`. Device integration is handled by `vpfe_get_pdata()`, async notifier callbacks, `vpfe_probe()`, `vpfe_remove()`, and sleep PM context save/restore helpers.

## Control Flow
Probe registers a V4L2 device, parses platform data or OF graph endpoint, maps the CCDC registers, requests the capture IRQ, enables runtime PM long enough to load CCDC defaults, allocates remote subdev slots, and registers an async notifier. When the remote subdevice binds, the driver matches its advertised media-bus codes against local formats, then completion initializes locks/queue/video node and sets input 0.

Open initializes the hardware only for the first file handle: it configures the default input, gets runtime PM, enables CONFIG, restores CCDC defaults, and clears interrupts. Release closes the CCDC and drops runtime PM on the last handle. Format setting asks the subdevice to set pad format, mirrors the returned mbus format into a V4L2 pix format, computes 32-byte-aligned stride/size, updates crop, and writes CCDC image configuration.

Streaming attaches CCDC interrupts, configures raw or YCbCr registers, pops the first queued buffer, writes its SDRAM address, enables the CCDC PCR bit, and starts the remote subdevice stream. The ISR handles VDINT0/VDINT1: progressive capture completes current buffers and schedules next buffers on half-frame interrupts, while interlaced capture tracks hardware field ID and optionally schedules bottom fields. Stop disables PCR, waits briefly for `capture_stop`, detaches interrupts, stops the subdevice, and returns all buffers.

## State And Persistence
In-memory state includes current subdevice/input, current format, crop rectangle, current/next capture buffers, DMA queue, field/sequence counters, CCDC configuration, field offset, runtime PM state, and saved CCDC register context for sleep. Hardware state is the CCDC register block, IRQ masks/status, SDRAM address, and subdevice stream state. No durable state is written.

## Dependencies And Integration Points
Depends on V4L2 core, async subdev notifier, fwnode endpoint parsing, media bus format APIs, videobuf2 DMA-contig, runtime PM, pinctrl PM, platform IRQ/MMIO resources, and a remote subdevice that supports pad format enumeration/setting, frame-size enumeration, optional standard ioctls, and `s_stream`.

## Risks
The implementation is effectively single-endpoint/single-input despite array abstractions. The async-bound comparison indexes the callback `asd` pointer as if it were an array; this is benign for one entry but risky if expanded. Raw Bayer pixel-format handling appears narrow and `vpfe_ccdc_get_pixel_format()` reports YUYV for raw mode, so raw-format paths need careful validation. Several ioctls reject changes while vb2 is busy, but standard/input/crop/format changes still rely on caller locking. Interlaced field synchronization can drop a frame during recovery. Runtime PM error handling in suspend/resume ignores late failures by design.

## Test Signals
Use `v4l2-compliance`, async graph probe with a real camera/decoder, media-bus code intersection tests, format set/get/try across all supported codes, crop selection, std query/set for analog decoders, streaming with at least three buffers, progressive and interlaced capture, buffer sequence/timestamp checks, private raw CCDC ioctl validation, runtime PM open/release cycles, and suspend/resume during active streaming.
