
# sources/distributed-fs/ceph-client/drivers/media/pci/tw5864/tw5864-video.c

## Purpose
This is the TW5864 V4L2 video/H.264 implementation. It initializes encoder tables and DMA buffers, registers one V4L2 capture device per input, configures analog decoder and H.264 encoder registers, manages vb2 queues, assembles software H.264 headers with hardware VLC output, and reports motion-detection events.

## Important APIs, Types, And Functions
Externally used functions are `tw5864_video_init`, `tw5864_video_fini`, `tw5864_prepare_frame_headers`, and `tw5864_request_encoded_frame`. Core vb2 callbacks are `tw5864_queue_setup`, `tw5864_buf_queue`, `tw5864_start_streaming`, and `tw5864_stop_streaming`. Control/ioctl handlers include `tw5864_s_ctrl`, format/std/input/parm handlers, `tw5864_subscribe_event`, and optional advanced debug register access. Frame completion is handled by `tw5864_handle_frame_work` and `tw5864_handle_frame`.

## Control Flow
`tw5864_video_init` allocates four coherent VLC/MV DMA frame buffers, uploads VLC and quantization tables, resets and clocks video input hardware, initializes encoder DMA base addresses, enables sensor/H.264 channels, sets bus maps, starts timer/VLC interrupts, initializes bottom-half work, and registers four video inputs. Streaming starts by enabling an input, choosing D1 geometry, programming indirect picture/crop registers and direct encoder/scaler/rate registers, then setting `enabled`. Timer ISR in the core calls `tw5864_request_encoded_frame`, which writes per-frame encoder state, prepares headers in the next user buffer, programs VLC bit alignment, selects raw/reconstructed buffers, and toggles `START_NSLICE`. VLC-done IRQ queues bottom-half work; the worker syncs coherent buffers, calls `tw5864_handle_frame`, inserts emulation-prevention bytes, sets payload/timestamp/sequence, optionally queues `V4L2_EVENT_MOTION_DET`, and completes the vb2 buffer.

## State And Persistence
Per-input state includes active vb2 list, current buffer, enabled flag, standard, dimensions, sequence counters, GOP/QP/frame interval, H.264 tail bits, register shadow values, current raw-buffer ID, and motion threshold grid. Device state includes the shared H.264 ring and work item. State is runtime-only; hardware registers hold active configuration until reset/unload.

## Dependencies And Integration Points
The file integrates V4L2 ioctls, controls, events, and `videobuf2-dma-contig`; TW5864 core IRQ scheduling; H.264 header helpers; indirect register helpers; and register definitions. Userspace sees H.264 capture devices supporting read, mmap, DMABUF, streaming, controls, frame intervals, and motion events.

## Risks
Only D1 resolution is effectively selected despite enum support for HD1/CIF/QCIF. `tw5864_video_input_init` writes indirect standard registers using `video_nr` rather than `input->nr`, which is notable if requested video node numbers differ from channel numbers. The encoder table upload writes forward then inverse quantization tables to the same base range, which should be verified against hardware expectations. Buffer handling depends on `tw5864_prepare_frame_headers` having reserved a vb2 buffer before VLC completion. Motion detection is heuristic and based on MV data from P-frames only.

## Test Signals
Exercise `v4l2-ctl --stream-mmap`, `--stream-user` is not supported here, read I/O, QP/GOP controls, standard query/set, frame interval changes, motion event subscription, and all four channels simultaneously. Decode output with FFmpeg/GStreamer, check SPS/PPS at GOP starts, verify no "vb is empty" or buffer-space drop logs, and test GOP size 1 for the documented quality workaround.
