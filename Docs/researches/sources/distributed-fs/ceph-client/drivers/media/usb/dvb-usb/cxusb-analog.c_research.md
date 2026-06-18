# sources/distributed-fs/ceph-client/drivers/media/usb/dvb-usb/cxusb-analog.c

## Purpose
Implements the optional analog/V4L2 half of the Conexant CXUSB Medion MD95700 hybrid DVB-T/analog capture driver. It registers `/dev/video*` and `/dev/radio*` devices, configures the CX25840 video decoder plus analog tuner/IF demodulator, receives BT.656 video over isochronous USB endpoint 2, converts that byte stream into UYVY vb2 capture buffers, and coordinates analog opens with the digital path through the shared `cxusb_medion_get()`/`cxusb_medion_put()` arbitration implemented in `cxusb.c`.

## Important APIs, Types, And Functions
The file consumes the shared `struct cxusb_medion_dev`, `struct cxusb_medion_auxbuf`, `struct cxusb_bt656_params`, and `struct cxusb_medion_vbuffer` declarations from `cxusb.h`. The main external entry points are `cxusb_medion_analog_init()`, `cxusb_medion_register_analog()`, and `cxusb_medion_unregister_analog()`. V4L2/vb2 integration is provided by `cxdev_video_qops`, `cxusb_video_ioctl`, `cxusb_radio_ioctl`, `cxusb_video_fops`, and `cxusb_radio_fops`.

Important internal groups are:

- Buffer setup: `cxusb_medion_v_queue_setup()`, `cxusb_medion_v_buf_init()`, and `cxusub_medion_v_buf_queue()` validate UYVY buffer sizing and maintain `cxdev->buflist`.
- Auxiliary stream buffering: `cxusb_auxbuf_*()` tracks the concatenated isochronous payload and trims old bytes when a new URB would exceed the auxiliary buffer.
- BT.656 parsing: `cxusb_medion_cf_refc_*()`, `cxusb_medion_copy_samples()`, `cxusb_medion_copy_field()`, and `cxusb_medion_v_process_auxbuf()` search SAV/EAV preambles, handle field changes, pad missing line samples, skip VBI data, and complete vb2 frames.
- URB lifecycle: `cxusb_medion_v_start_streaming()`, `cxusb_medion_v_complete()`, `cxusb_medion_v_complete_work()`, `cxusb_medion_v_complete_handle_urb()`, `cxusb_medion_v_stop_streaming()`, and `cxusb_medion_urbs_free()` allocate isochronous URBs, resubmit them from workqueue context, and tear them down.
- Analog controls: format, input, tuner, frequency, standard, and status ioctls are implemented by `cxusb_medion_*fmt*`, `cxusb_medion_*input*`, `cxusb_medion_*tuner*`, `cxusb_medion_*frequency*`, `cxusb_medion_*std*`, and `cxusb_medion_log_status()`.

## Control Flow
Registration starts in `cxusb_medion_register_analog()`: initialize `dev_lock`, a V4L2 release completion, register `v4l2_device`, attach subdevices with `cxusb_medion_register_analog_subdevs()`, initialize URB work and the queued-buffer list, set a conservative 320x240 default capture size, then register the video and radio devices. Subdevice registration attaches the CX25840 at `0x44`, the tuner at `0x61`, and the TDA9887-compatible IF demod at `0x43`, then configures the tuner type and CX25840 BT.656 output mode.

Open flow is deliberately routed through the shared Medion mode gate. `cxusb_videoradio_open()` calls `cxusb_medion_get(dvbdev, CXUSB_OPEN_ANALOG)` before `v4l2_fh_open()`, causing the core driver to power the device, switch USB alternate setting/mode to analog, and run `cxusb_medion_analog_init()` if analog was not already active. Release calls `vb2_fop_release()` for video or `v4l2_fh_release()` for radio, then decrements the shared open counter with `cxusb_medion_put()`.

Streaming starts through vb2. `cxusb_medion_v_start_streaming()` determines field order, starts CX25840 streaming, sends `CMD_STREAMING_ON`, allocates an auxiliary buffer sized around one frame plus one URB, allocates up to five isochronous URBs, and submits them. USB completion only records which URB completed and schedules work. The work handler runs under the video-device lock, appends completed URB payloads into the auxiliary buffer, parses enough BT.656 data to complete frames, resubmits URBs, and reschedules itself while buffered data can produce more frames. Stop flow sends `CMD_STREAMING_OFF`, stops the CX25840, temporarily drops the video lock so completions can drain, kills all URBs, flushes the work item, frees buffers, returns outstanding vb2 buffers with error state, and clears `stop_streaming`.

## State And Persistence
Persistent in-kernel state lives in `struct cxusb_medion_dev`: current V4L2 input, norm, width/height, field order, stop flag, auxiliary stream bytes, URB pointers/completion bitmap, current BT.656 parser position, active vb2 buffer, frame sequence, queued buffer list, V4L2 subdevice pointers, and video/radio device pointers. There is no disk persistence. Device-visible state is changed through USB vendor commands, USB alternate-interface selection done by `cxusb.c`, I2C writes to the tuner, and V4L2 subdevice operations on CX25840/tuner/TDA9887.

## Dependencies And Integration Points
The file depends on the media core, V4L2 subdev API, videobuf2-vmalloc, CX25840 driver interface definitions, tuner framework, and the DVB USB CXUSB core. It is compiled only when `CONFIG_DVB_USB_CXUSB_ANALOG` enables the declarations in `cxusb.h`; otherwise the public analog hooks become stubs. It integrates tightly with `cxusb.c`: `cxusb_probe()` registers analog support only for the Medion device, `cxusb_medion_get()` calls `cxusb_medion_analog_init()` during analog mode acquisition, and disconnect calls `cxusb_medion_unregister_analog()`.

## Risks
The largest risk area is concurrency between vb2 stop, URB completions, and workqueue parsing; the code explicitly drops/reacquires the video lock and uses `usb_kill_urb()` plus `flush_work()` to manage this. Auxiliary buffer overwrite resets the current frame parser, so high USB jitter or slow workqueue processing can skip frames. The BT.656 parser pads malformed or early field/line transitions with zeroes, which is robust for frame completion but can hide signal timing problems. Mode switching shares hardware with the DVB frontend, so any missed `cxusb_medion_put()` or failed acquisition can block analog or digital users. Radio support is intentionally incomplete because audio support is still TODO.

## Test Signals
Useful test signals are successful creation/removal of video and radio nodes on Medion MD95700 probe/disconnect, analog open returning `-EBUSY` while digital streaming owns the device, `VIDIOC_QUERYCAP`/format/input/std/frequency operations succeeding through V4L2 compliance tools, stable `vb2` streaming with queued buffers receiving monotonically increasing UYVY frames, clean stream stop without URB resubmit errors or leaked buffers, and kernel logs from `CXUSB_DBG_BT656`, `CXUSB_DBG_URB`, `CXUSB_DBG_OPS`, and `CXUSB_DBG_AUXB` when diagnosing malformed BT.656 streams.
