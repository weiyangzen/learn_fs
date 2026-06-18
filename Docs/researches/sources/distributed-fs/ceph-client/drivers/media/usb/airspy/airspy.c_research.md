# sources/distributed-fs/ceph-client/drivers/media/usb/airspy/airspy.c

## Purpose
Implements the USB Video4Linux2 SDR driver for AirSpy receivers. It exposes the device as a V4L2 SDR capture node, translates V4L2 tuner/frequency/control operations into AirSpy vendor control messages, and streams raw 12-bit little-endian SDR samples from bulk endpoint `0x81` into videobuf2 buffers.

## Important APIs, types, and functions
The central state is `struct airspy`, which owns USB device pointers, a `video_device`, `v4l2_device`, `vb2_queue`, queued buffer list, streaming URBs, DMA buffers, current SDR format, ADC/RF frequencies, and V4L2 tuner gain controls. `airspy_ctrl_msg()` is the vendor command dispatcher for receiver mode, frequency, board/version reads, and gain/AGC controls. `airspy_start_streaming()` allocates coherent bulk buffers, builds URBs, submits them, then sends `CMD_RECEIVER_MODE` on. `airspy_urb_complete()` copies each completed bulk payload into the next queued vb2 buffer via `airspy_convert_stream()`. IOCTL handlers implement SDR format enumeration/get/set/try, tuner info, frequency bands, and frequency updates. Probe registers controls and the SDR video node; disconnect marks the device gone and unregisters it.

## Control flow and state
Probe allocates `struct airspy`, reads board ID/version, initializes vb2, V4L2 controls, and registers a `VFL_TYPE_SDR` device. Streaming begins through vb2 `start_streaming`: set `POWER_ON`, allocate six 64 KiB buffers and URBs, submit them, then enable receiver mode. URB callbacks run in atomic context, pop one queued frame buffer under `queued_bufs_lock`, copy bytes, set payload/timestamp/sequence, complete the vb2 buffer, and resubmit the URB. Stop streaming sends receiver mode off, kills/frees URBs and stream buffers, returns queued buffers with error, and clears `POWER_ON`.

## Dependencies and integration points
Depends on USB core, V4L2 device/ioctl/control/event APIs, vb2-vmalloc memory, and SDR pixel format `V4L2_SDR_FMT_RU12LE`. User space sees standard V4L2 read, mmap, poll, ioctl, streaming, tuner, frequency, and control interfaces. Hardware integration is through AirSpy vendor USB control requests and one bulk IN endpoint.

## Risks and test signals
`airspy_ctrl_msg()` chooses IN transfer direction for several setter commands, matching existing firmware API behavior but making command direction a key hardware compatibility risk. Streaming has drop behavior when no vb2 buffers are queued, tracked by `vb_full`. Race-sensitive areas are disconnect versus queued buffers, URB resubmission after errors, and lock ordering between `v4l2_lock` and `vb_queue_lock`. Test signals include successful probe/version logs, V4L2 capability and SDR format enumeration, setting RF frequency and gain controls, sustained stream-on/stream-off without URB leaks, monotonic frame sequence, sample-rate debug output, and no buffer overrun/drop messages under adequate user buffer depth.
