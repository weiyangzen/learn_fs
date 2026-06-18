<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.c

## Purpose

This file implements the DaVinci VPIF display/output V4L2 driver for channels 2 and 3. It registers output video nodes, attaches encoder subdevices from platform data, handles output/standard/DV timing/format ioctls, queues user buffers through vb2 DMA-contig, programs VPIF display timing/address registers, and advances frames in the VPIF ISR.

## Important APIs, types, and functions

- `vpif_ioctl_ops` exposes output querycap, video-output format, streaming, standard, output selection, DV timing, and log-status ioctls.
- `vpif_buffer_queue_setup()`, `vpif_buffer_prepare()`, `vpif_buffer_queue()`, `vpif_start_streaming()`, and `vpif_stop_streaming()` are vb2 output operations.
- `vpif_channel_isr()`, `process_progressive_mode()`, and `process_interlaced_mode()` complete displayed buffers and schedule the next buffer.
- `vpif_update_std_info()`, `vpif_update_resolution()`, `vpif_calculate_offsets()`, and `vpif_config_addr()` derive display geometry and hardware address callbacks.
- `vpif_set_output()` maps user output indices to subdevices and routes encoder inputs/outputs.

## Control flow

Probe requires platform data, allocates two display channel objects, registers the V4L2 device, requests optional IRQs, registers I2C encoder subdevices, assigns group IDs, and completes probe by initializing each channel, selecting output 0, setting NTSC default resolution, initializing vb2, and registering video-output nodes numbered around channels 2 and 3.

Stream-on locks the queue, optionally programs the board clock for SD/HD and mux mode, calls common `vpif_set_video_params()` for hardware channel `channel_id + 2`, chooses the address callback, takes the first queued buffer, writes Y/C top/bottom addresses, enables interrupts/channels, and enables clipping where configured. The ISR ignores the first field interrupt, then in progressive mode completes the previous displayed buffer and programs the next; in interlaced mode it syncs hardware FID against software state and alternates completion/scheduling by field.

## State and persistence behavior

The static `vpif_obj` stores the V4L2 device, channel objects, subdevice array, and display platform config. Each channel stores selected output, current encoder subdevice, current standard/timings, VPIF parameters, and one common vb2/DMA state object. There is no persistence beyond the loaded driver instance.

## Dependencies and integration points

It depends on common VPIF exports, V4L2/vb2 DMA-contig, platform data with display channel configs, board clock callback `set_clock`, optional clipping flags, and I2C encoder subdevices such as those selected by Kconfig.

## Risks and edge cases

Unlike capture, display has no DT async path in this file and gives up without platform data. Only YUV422P is exposed. Global `ycmux_mode` affects channel 3 when channel 2 uses two-channel output. Buffer alignment must be 8-byte clean. Stop streaming returns active and queued buffers as errors and assumes stream-on initialized `cur_frm`/`next_frm`.

## Test signals

Validate output enumeration/selection, standard switching, DV timing setup, clipping-enabled channels, progressive/interlaced output, channel 2 two-channel mux behavior, MMAP/USERPTR/DMABUF queues, IRQ handling, and suspend/resume while streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif_display.c -->
