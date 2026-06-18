# sources/distributed-fs/ceph-client/drivers/media/platform/amlogic/c3/isp/c3-isp-capture.c

## Purpose

`c3-isp-capture.c` implements the capture video nodes for the Amlogic C3 ISP driver. It exposes three memory capture devices, validates their media links against upstream resizer output, programs WRMIFX3 write-memory-interface registers, manages vb2 DMA-contig capture buffers, and completes frames from the ISP interrupt path.

## Important APIs, Types, And Functions

- `cap_formats[]` maps supported media bus codes and V4L2 pixel formats to WRMIFX3 hardware format bits, plane layout, input bit depth, UV swap, and chroma subsampling. Supported outputs include GREY, NV12M, NV21M, NV16M, NV61M, and several 12-bit Bayer formats stored as 16-bit raw.
- Register helpers: `C3_ISP_WRMIFX3_REG()`, `c3_isp_cap_wrmifx3_buff()`, `c3_isp_cap_wrmifx3_format()`, `c3_isp_cap_start()`, and `c3_isp_cap_stop()` program buffer addresses, format/window/stride fields, and top-level path enables.
- Buffer helpers: `c3_isp_cap_dummy_buff_create()`, `c3_isp_cap_dummy_buff_destroy()`, `c3_isp_cap_cfg_buff()`, `c3_isp_cap_done()`, and `c3_isp_cap_return_buffers()`.
- V4L2 ioctl handlers: querycap, enum format, get/set/try multiplanar format, enum frame sizes, event subscribe/unsubscribe, and standard vb2 ioctls.
- Media graph validation: `c3_isp_cap_link_validate()` compares upstream subdev active format against capture dimensions and expected mbus code.
- vb2 operations: queue setup, buffer init, buffer prepare, queue, start streaming, and stop streaming.
- Registration APIs: `c3_isp_captures_register()`, `c3_isp_captures_unregister()`, and `c3_isp_captures_isr()`.

## Control Flow

Registration iterates over `C3_ISP_CAP_DEV_0..2`, initializes default 1920x1080 NV12M format, binds each capture device to the matching resizer, initializes locks and pending lists, and registers a `video_device` with a sink media pad and a DMA-contig vb2 queue.

Format setting calls `c3_cap_try_fmt()`, which clamps dimensions to 160x120 through 2888x2240, selects a supported format, sets fixed field/colorimetry defaults, determines memory-plane count from `v4l2_format_info()`, aligns bytesperline to 16 bytes, and computes per-plane `sizeimage`. Link validation later ensures the capture format matches the upstream subdev source format and media bus code.

Streaming starts by starting the media pipeline, allocating a dummy DMA buffer for frame drops/no-buffer cases, runtime-resuming the ISP device, programming the current buffer and format into WRMIFX3, enabling the WRMIF path, and enabling streams on the matching resizer source pad. Streaming stops in reverse: disable WRMIF path, return current/pending buffers with error, disable upstream streams, runtime-put the device, destroy the dummy buffer, and stop the media pipeline.

Queued vb2 buffers are appended to `cap->pending` under `buff_lock`. At frame completion, `c3_isp_captures_isr()` calls `c3_isp_cap_done()` for all three capture devices. The active buffer gets sequence/timestamp/field metadata and is completed with `VB2_BUF_STATE_DONE`; the next pending buffer is selected and programmed, or the dummy buffer is used if no pending buffer exists.

## State And Persistence

Each `struct c3_isp_capture` stores its id, vb2 queue, video node, media pad, mutex, parent ISP pointer, associated resizer, dummy buffer, current active buffer, spinlock-protected pending list, and active pixel format. State is volatile driver runtime state. The dummy buffer is DMA memory allocated only while streaming. Frame sequence comes from the parent `isp->frm_sequence`.

## Dependencies And Integration Points

The file depends on V4L2 controls/events/ioctls/media-controller helpers, vb2 DMA-contig, runtime PM, common C3 ISP state from `c3-isp-common.h`, and register bit definitions from `c3-isp-regs.h`. It integrates with resizer subdevices via `v4l2_subdev_enable_streams()`/`disable_streams()` and with the top-level device ISR through `c3_isp_captures_isr()`.

## Risks

`c3_isp_cap_dummy_buff_destroy()` frees unconditionally and assumes a successful prior allocation; error paths currently call it only after create success, but future changes should preserve that invariant. The dummy buffer uses the maximum of Y and UV plane sizes and maps both hardware channels to the same DMA address when no buffer is active; this is intentional for dropping output but must be large enough for both channels. The capture ISR completes all three captures on every call, so top-level IRQ filtering must ensure this corresponds to frame completion. `c3_isp_cap_s_fmt_mplane()` does not reject format changes while buffers are busy, so callers may need external serialization or vb2 busy checks if format changes during streaming are possible. Link validation relies on upstream active format being available.

## Test Signals

Run media-ctl graph validation, `v4l2-compliance` on all three capture nodes, streaming tests for each supported pixel format, no-buffer streaming tests to exercise dummy buffers, DMABUF and MMAP capture tests, runtime PM start/stop tests, frame sequence/timestamp checks, and negative tests for mismatched upstream mbus code or dimensions. Register programming can be checked with hardware traces or debug instrumentation around WRMIFX3 address/format writes.
