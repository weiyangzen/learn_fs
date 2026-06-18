# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/vicam.c

## Purpose
`vicam.c` is a GSPCA subdriver for ViCam USB cameras. Unlike many GSPCA webcam drivers, it does not rely on normal isochronous packet scanning. It uploads Intel HEX firmware to the device, powers the camera on, schedules a sleeping workqueue loop, sends a per-frame capture request with exposure/gain/scale settings, bulk-reads an entire frame plus a fixed header, strips that header, and hands the frame to the GSPCA core.

## Important APIs, Types, and Data
`struct sd` embeds `struct gspca_dev` and a `work_struct` used by the streaming loop. `VICAM_FIRMWARE` names the required firmware file `vicam/firmware.fw`, declared with `MODULE_FIRMWARE()`.

`vicam_mode[]` exposes Bayer `V4L2_PIX_FMT_SGRBG8` modes: 256x122, 256x200, 256x240, and 512x244. The comments explain that the sensor has unusual non-square pixel behavior and that the modes are chosen around the optics and original 512x244 sensor readout.

The key helpers are `vicam_control_msg()`, `vicam_set_camera_power()`, `vicam_read_frame()`, and `vicam_dostream()`. GSPCA callbacks are `sd_config()`, `sd_init()`, `sd_start()`, `sd_stop0()`, and `sd_init_controls()`.

## Control Flow
`sd_config()` marks the camera as bulk (`cam->bulk = 1`) with a small GSPCA bulk buffer because the driver allocates its own per-frame buffer. It installs `vicam_mode[]` and initializes the work item with `vicam_dostream()`.

`sd_init()` runs at probe and resume. It loads the IHEX firmware with `request_ihex_firmware()`, allocates a page buffer, iterates each binary record with `ihex_next_binrec()`, rejects records larger than one page, copies the record bytes, and sends them to the device with vendor request `0xff`. Firmware is released before return.

`sd_start()` powers the camera with request `0x50` and, when enabling, request `0x55`, then schedules the stream work item.

`vicam_dostream()` allocates `sizeimage + HEADER_SIZE`, loops while the device is present and streaming, exits during PM freeze, calls `vicam_read_frame()`, discards the 64-byte frame header, and adds a complete frame with `FIRST_PACKET` followed by `LAST_PACKET`. It frees the buffer on exit.

`vicam_read_frame()` builds a 16-byte request in `gspca_dev->usb_buf`: byte 0 is gain, byte 1 contains x/y scaling bits, byte 3 encodes height class, bytes 4-7 encode exposure either as partial-frame exposure below 256 or frame-rate-modifying exposure at 256 and above, and byte 8 centers the vertical crop. It sends request `0x51` while holding `usb_lock`, then bulk-reads from endpoint `0x81` with a 10-second timeout and requires the actual length to match exactly.

`sd_stop0()` is called with `usb_lock` held. It deliberately unlocks around `flush_work()` so the worker can finish USB operations, relocks, and powers the camera down if still present.

## State and Persistence
Runtime state is minimal: the scheduled work item plus GSPCA core flags (`present`, `streaming`, `frozen`) and V4L2 exposure/gain controls. The firmware is loaded into device RAM on probe/resume and is not persisted by the driver. Per-frame request state is rebuilt for every capture, so control changes naturally apply on the next `vicam_read_frame()` loop without a separate `.s_ctrl` callback.

## Dependencies and Integration Points
The driver depends on Linux firmware/IHEX support (`request_ihex_firmware`, `ihex_next_binrec`), USB vendor control and bulk transfers, GSPCA frame assembly, and V4L2 controls. The USB table binds IDs `04c1:009d` and `0602:1001`.

The camera appears as a bulk GSPCA camera but bypasses GSPCA packet scanning entirely; the only frame-delivery path is the workqueue function. This makes the lock/unlock behavior in `sd_stop0()` an important integration point with the GSPCA core.

## Risks and Edge Cases
Streaming allocates one full frame buffer at start of the worker loop. Allocation failure logs an error and exits without a direct start failure because allocation occurs asynchronously after `sd_start()` has returned.

Bulk read requires `act_len == size`. Short reads are treated as `-EIO`, which is appropriate for complete-frame reads but can make transient USB behavior terminate streaming.

The firmware path is mandatory. Missing or invalid `vicam/firmware.fw` prevents initialization. Records over `PAGE_SIZE` are rejected.

The comments note that bytes 2 and 9-15 are poorly understood. Exposure/scaling values are reverse engineered, so mode or control changes require real hardware validation.

## Test Signals
Primary signals are successful firmware load, no `control msg req` errors, successful `sd_start()` power-on, recurring full-length bulk reads from endpoint `0x81`, and delivered frames whose payload sizes match selected `sizeimage` after header stripping.

Tests should include missing firmware handling, resume firmware reload, start/stop while the worker is blocked in a bulk read, PM freeze exit, all four modes, exposure values below and above 256, gain extremes, and disconnect during streaming.
