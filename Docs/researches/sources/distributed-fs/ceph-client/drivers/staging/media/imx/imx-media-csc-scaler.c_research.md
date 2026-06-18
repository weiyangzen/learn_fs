# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-csc-scaler.c

## Purpose

`imx-media-csc-scaler.c` implements a V4L2 mem2mem video device for the i.MX IPUv3 Image Converter post-processor. It provides color-space conversion, scaling, cropping/composition, and rotation/flip controls over paired OUTPUT and CAPTURE queues.

## Important APIs, Types, and Functions

`struct ipu_csc_scaler_priv` owns the video node, media device pointer, V4L2 mem2mem device, and mutex. `struct ipu_csc_scaler_ctx` is per-open state with a V4L2 file handle, source/destination queue data, image-convert context, controls, rotation mode, and sequence counter. Public lifecycle functions are `imx_media_csc_scaler_device_init()`, `imx_media_csc_scaler_device_register()`, and `imx_media_csc_scaler_device_unregister()`.

Important callbacks are `device_run()`, `job_abort()`, `ipu_ic_pp_complete()`, `ipu_csc_scaler_try_fmt()`, `ipu_csc_scaler_s_fmt()`, `ipu_csc_scaler_s_selection()`, `ipu_csc_scaler_start_streaming()`, `ipu_csc_scaler_stop_streaming()`, and `ipu_csc_scaler_s_ctrl()`.

## Control Flow

Open allocates a context, initializes a mem2mem context with two vb2 DMA-contiguous queues, installs hflip/vflip/rotate controls, and seeds both queues with a 720x576 YUV420 format. Format try/set passes source and destination images through `ipu_image_convert_adjust()` to align sizes, strides, and rotation constraints. Streaming prepare waits until both queues are streaming, then calls `ipu_image_convert_prepare()` using `md->ipu[0]`.

When the mem2mem scheduler runs a job, `device_run()` reads the next source/destination buffers, allocates an `ipu_image_convert_run`, fills physical DMA addresses, and queues conversion. Completion removes both buffers, copies metadata, assigns matched sequence numbers, reports done or error based on `run->status`, finishes the mem2mem job, and frees the run object.

## State and Persistence Behavior

State is per-open context and per-device registration only. No settings persist beyond file lifetime. The active image-convert context exists only while both queues stream and is unprepared on streamoff. Rotation and flips can force queue format changes and are rejected with `-EBUSY` if already-allocated queues would need incompatible dimensions or strides.

## Dependencies and Integration Points

The driver depends on V4L2 mem2mem, vb2 DMA-contig, V4L2 controls/events, and IPUv3 image-convert APIs. The main `imx-media` platform driver creates and registers the device after async probe completion, once IPU handles have been recorded by CSI binding.

## Risks and Edge Cases

`ipu_image_from_q_data()` maps default quantization into `ycbcr_enc` in both colorimetry branches, which looks suspicious because quantization is not assigned in the second branch. The scaler assumes `md->ipu[0]` is present, so systems where only another IPU is populated may fail. `device_run()` allocates per job and must correctly clean up on queue failure; the error path completes both buffers as error. Capture colorimetry cannot be set independently by API design.

## Test Signals

Test paired stream-on ordering, queue allocation before and after rotation changes, crop/compose bounds and 8-pixel alignment, RGB/YUV conversions, sizeimage and bytesperline adjustment, hflip/vflip/90-degree rotations, abort while a conversion is active, conversion completion error status, and device registration after probe completion.
