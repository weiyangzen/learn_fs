# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc-base.c

## Purpose
This file is the shared V4L2/vb2/media-controller base for deprecated Atmel/Microchip ISC and XISC platform drivers. It handles format negotiation with a sensor subdevice, pipeline and DMA programming through SoC callbacks, video node registration, vb2 capture queues, streaming start/stop, DMA and histogram interrupts, auto white balance, V4L2 controls, async subdevice binding, and common regmap/pipeline initialization.

## Important APIs and Functions
Vb2 operations include `isc_queue_setup()`, `isc_buffer_prepare()`, `isc_start_streaming()`, `isc_stop_streaming()`, and `isc_buffer_queue()`. V4L2 ioctl support includes format enumeration/get/set/try, input operations, stream parameters, frame size enumeration, and vb2 ioctl forwarding. File operations `isc_open()` and `isc_release()` manage file handles and subdevice power.

Format negotiation is centered on `isc_try_fmt()` and `isc_set_fmt()`. `isc_try_fmt()` chooses a sensor media-bus format from supported subdevice formats, optionally prefers direct sensor output via `sensor_preferred`, validates whether requested output is compatible with RAW/GREY/YUV/RGB input, configures RLP/DMA fields with `isc_try_configure_rlp_dma()`, computes pipeline bits with `isc_try_configure_pipeline()`, asks the subdevice for a try format, and fills bytesperline/sizeimage. `isc_set_fmt()` applies the active subdevice format and promotes `try_config` to `config`.

Streaming configuration is handled by `isc_configure()`, `isc_set_pipeline()`, `isc_update_profile()`, `isc_crop_pfe()`, and `isc_start_dma()`. The SoC-specific driver supplies callbacks for DPC, CSC, CBC, CC, GAM, RLP, controls, and pipeline adaptation. `atmel_isc_interrupt()` retires DMA buffers on `ISC_INT_DDONE`, queues the next buffer, completes stop waits, and schedules AWB work on `ISC_INT_HISDONE`.

Auto white balance uses histogram helpers `isc_set_histogram()`, `isc_hist_count()`, `isc_wb_update()`, and `isc_awb_work()`. V4L2 controls are initialized in `isc_ctrl_init()`, with normal brightness/contrast/gamma controls and a clustered auto-white-balance/manual gains/offsets/do-white-balance set.

Async integration uses `atmel_isc_async_ops`: `isc_async_bound()` stores the single supported sensor, `isc_async_complete()` initializes work, vb2 queues, formats, controls, and registers the video node, and `isc_async_unbind()` unregisters and frees resources. Exported APIs are `atmel_isc_interrupt()`, `atmel_isc_async_ops`, `atmel_isc_subdev_cleanup()`, `atmel_isc_pipeline_init()`, and `atmel_isc_regmap_config`.

## Control Flow and State
Probe in the SoC file creates `struct isc_device`, then async notifier completion in this base constructs runtime media state. Open powers the sensor and reapplies the current format. `VIDIOC_S_FMT` is blocked while vb2 is busy. Streamon starts the sensor, resumes runtime PM, configures PFE/RLP/DMA/pipeline/histogram, enables DMA-done interrupts, selects the first queued buffer, crops the front-end to requested size, and starts DMA. Interrupts complete frames and advance the queue. Streamoff sets `stop`, waits for current-frame completion, disables DMA IRQs, runtime-suspends the device, stops the subdevice, and returns active/queued buffers with error.

Persistent driver state lives in `struct isc_device`: active and try format config, current V4L2 format, supported format list, vb2 queue and DMA queue, current frame pointer, sequence counter, stop/completion state, controls and histogram state, locks, current sensor, pipeline regmap fields, and SoC callback pointers. Hardware state is persisted in ISC registers and subdevice state while the device is active.

## Dependencies and Integration Points
This base depends on V4L2 device/subdev/fwnode/control/event/ioctl APIs, videobuf2 DMA-contig, media controller async notifier, regmap/regmap fields, runtime PM, platform IRQs, and SoC-specific callbacks and register offsets from `atmel-isc.h`. It integrates with SAMA5D2 and SAMA7G5 files through exported functions and shared `struct isc_device`.

## Risks and Test Signals
Risks include complex format fallback behavior, RAW-only assumptions for AWB, racing AWB register updates with DMA capture, buffer queue underflow, streamoff timeouts, one-sensor-only enforcement, error paths that must unwind mutex/work/control/video resources, and deprecated code diverging from newer Microchip ISC behavior. Test signals include media graph binding, video node registration, `v4l2-compliance`, format try/set across RAW/YUV/RGB/GREY, vb2 streaming with multiple buffers, DMA-done interrupt frame sequencing, streamoff timeout absence, AWB auto and one-shot behavior, runtime PM balance, and clean async unbind/remove.
