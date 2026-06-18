# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-video.c

## Purpose
`ipu6-isys-video.c` implements IPU6 ISYS V4L2 capture video nodes and the firmware stream lifecycle behind them. It exposes video and metadata capture formats, validates media links, computes DMA buffer sizes, configures firmware stream pins, starts/stops upstream subdev streams, manages stream handles, and contributes per-stream data-rate information for iWake watermark programming.

## Important APIs, Types, And Functions
The exported format table `ipu6_isys_pfmts[]` maps V4L2 pixel/meta formats to media-bus codes, packed/unpacked bit depths, firmware frame formats, and metadata flags. Major functions are `ipu6_isys_get_isys_format()`, `ipu6_isys_video_prepare_stream()`, `ipu6_isys_video_set_streaming()`, `ipu6_isys_fw_open()`, `ipu6_isys_fw_close()`, `ipu6_isys_setup_video()`, `ipu6_isys_video_init()`, `ipu6_isys_video_cleanup()`, stream lookup helpers, watermark helpers, and getters for current format/size/stride/dimensions.

## Control Flow
VIDIOC format calls clamp dimensions to ISYS limits, align bytes-per-line to 64 bytes, and over-allocate `sizeimage` by at least one line or the platform DMA overshoot value to avoid hardware DMA overrun. `ipu6_isys_setup_video()` finds the active route on the remote CSI-2 subdev, determines source stream, gets CSI-2 frame descriptor data when available, starts the media pipeline, and reserves or shares a firmware stream based on CSI source and virtual channel.

Streaming starts in `ipu6_isys_video_set_streaming()`. It maps the video pad route back to the sink stream, opens/configures firmware with `start_stream_firmware()`, then enables V4L2 subdev streams with the pipeline stream mask. Firmware open builds `ipu6_fw_isys_stream_cfg_data_abi` by adding input/output pins for every queue in the shared stream; optional first buffers are sent with `STREAM_START_AND_CAPTURE`. Stop sends firmware flush, disables upstream streams, closes firmware, and releases the stream-open count.

## State And Persistence
Video node state includes current video/meta formats, selected stream pointer, source stream, virtual channel/data type, and watermark parameters. ISYS firmware communication is reference counted in `isys->ref_count`; the first open configures SPC and initializes firmware communication, while the last close tears it down or marks `need_reset` if firmware context remains.

## Dependencies And Integration Points
This file ties together V4L2 file/ioctl APIs, vb2 queues, media pipelines, V4L2 subdev streams, CSI-2 frame descriptors, IPU6 CPD/SPC firmware setup, IPU6 firmware ABI commands, runtime PM, and iWake watermark calculation in `ipu6-isys.c`.

## Risks And Test Signals
Risk centers on graph/route assumptions and firmware sequencing. `ipu6_isys_fw_pin_cfg()` assumes locked active state and valid remote pads; bad route state can propagate to firmware pin counts. Stream sharing by virtual channel and subdevice must release refcounts exactly. `video_open()` blocks when `need_reset` is set, so tests need recovery through runtime suspend. Test media graphs with multiple CSI source pads, metadata capture, frame descriptors absent/present, unsupported mbus codes, format changes while queues are busy, stream-on failure after firmware open, and iWake data-rate calculations for sensors without link-frequency controls.
