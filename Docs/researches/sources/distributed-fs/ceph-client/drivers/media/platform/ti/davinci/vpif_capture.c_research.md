<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.c

## Purpose

This file implements the DaVinci VPIF capture V4L2 driver for channels 0 and 1. It registers capture video nodes, binds decoder/sensor subdevices through legacy I2C board data or DT async notifier, handles V4L2 input/standard/DV timing/format ioctls, manages vb2 DMA-contig buffers, and services VPIF frame interrupts.

## Important APIs, types, and functions

- `vpif_ioctl_ops` exposes capture querycap, format, input, streaming, standard, DV timing, and log-status ioctls.
- `vpif_buffer_queue_setup()`, `vpif_buffer_prepare()`, `vpif_buffer_queue()`, `vpif_start_streaming()`, and `vpif_stop_streaming()` are vb2 capture operations.
- `vpif_channel_isr()` handles frame interrupts and advances buffers for progressive and interlaced modes.
- `vpif_update_std_info()`, `vpif_calculate_offsets()`, and `vpif_config_addr()` derive VPIF timing, field layout, pitch, and register address callbacks from selected standard/format.
- `vpif_set_input()` routes selected inputs through board/DT path callbacks and subdevice `s_routing`.
- `vpif_capture_get_pdata()` builds capture platform data from OF graph endpoints when board data is absent.

## Control flow

Probe allocates two channel objects, registers a V4L2 device, requests optional IRQ resources per channel, obtains platform data or builds it from DT endpoints, allocates the subdevice pointer table, and either registers I2C subdevices immediately or registers a V4L2 async notifier. Completion initializes each channel, selects input 0, sets NTSC default format, initializes vb2, and registers `/dev/video0` and `/dev/video1` style capture nodes.

On stream-on, the driver configures board-specific input channel mode, starts the current subdevice stream, calls common `vpif_set_video_params()`, chooses the address programming helper, pulls the first queued buffer, writes its top/bottom Y/C addresses, enables field interrupts, and enables channel 0 plus channel 1 if needed for two-channel mode. The ISR ignores the first interrupt, then for progressive frames completes the current buffer and schedules the next; for interlaced frames it synchronizes software field ID with hardware FID and alternates completion/scheduling on even/odd fields.

## State and persistence behavior

The static `vpif_obj` owns the V4L2 device, two channel objects, subdevice table, async notifier, and platform config. Each channel stores selected input, current subdevice, standard/timing, VPIF parameters, and one `common_obj` with vb2 queue, DMA queue, active/next buffers, field offsets, and a selected `set_addr` function. There is no disk persistence; defaults are recreated on probe.

## Dependencies and integration points

It depends on common VPIF exports from `vpif.c`/`vpif.h`, videobuf2 DMA-contig, V4L2 ioctl/fwnode/async/subdev APIs, OF graph parsing, I2C subdevice registration, and DaVinci VPIF platform data callbacks such as `setup_input_channel_mode` and `setup_input_path`.

## Risks and edge cases

The driver uses global `ycmux_mode` and `channel_first_int`, so simultaneous channel streams can interact in two-channel modes. Buffer addresses and field offsets must be 8-byte aligned. Raw Bayer paths bypass the standard table and set CCD/raw capture mode, while NV16 paths use VPIF timing tables. `vpif_stop_streaming()` assumes `cur_frm` is valid after stream-on. DT data construction indexes channel inputs with `i`, making endpoint ordering important.

## Test signals

Validate input enumeration/selection, standard and DV timing ioctls, raw Bayer sensor capture, BT.656 decoder capture, progressive and interlaced streaming, DMABUF/MMAP/USERPTR queues, insufficient/unaligned buffer rejection, IRQ sharing, suspend/resume during streaming, and async notifier binding with DT endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_capture.c -->
