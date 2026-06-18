# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu-dec.c

## Purpose
`wave5-vpu-dec.c` is the V4L2 mem2mem decoder frontend for Wave5 hardware. It exposes a stateful decoder video device, handles userspace ioctls and vb2 queues, feeds compressed bitstream into a firmware ring buffer, manages capture framebuffers, reacts to firmware completion, and reports EOS or dynamic resolution changes.

## Important APIs, Data, and Functions
The file defines decoder format tables for HEVC/H264 compressed OUTPUT and multiple raw CAPTURE formats. Important functions include state management (`switch_state`, `set_instance_state`), source consumption (`wave5_handle_src_buffer`), EOS handling (`wave5_vpu_dec_stop`, `send_eos_event`, `flag_last_buffer_done`), dynamic resolution handling (`handle_dynamic_resolution_change`), result completion (`wave5_vpu_dec_finish_decode`), ioctl handlers for format/selection/decoder commands, vb2 operations, ring-buffer fill/write helpers, mem2mem operations (`device_run`, `job_ready`, `job_abort`), open/release, and device register/unregister.

## Control Flow
Opening allocates a `vpu_instance`, V4L2 file handle, mem2mem context, controls, default formats, IRQ FIFO, instance id, optional SRAM, and links the instance into the device list. OUTPUT stream start allocates a bitstream ring buffer and opens a firmware decoder instance. The first mem2mem job fills the ring buffer, issues sequence init, waits for interrupt, reads initial info, and queues a source-change event. CAPTURE setup prepares compressed internal framebuffers and linear user buffers, then picture jobs submit decode commands. IRQ-thread completion calls `finish_process`, gets output info, advances consumed source buffers, returns displayed capture buffers, and handles EOS or resolution changes.

## State and Persistence
Instance state includes the VPU state machine (`NONE`, `OPEN`, `INIT_SEQ`, `PIC_RUN`, `STOP`), source/destination formats, colorimetry, bitstream DMA ring, read pointer tracking, remaining consumed bytes, queued counts, EOS/draining flags, framebuffer arrays, FBC allocation counts, display flags, and source-feed list protected by `feed_lock`. State persists across streaming transitions until release, with streamoff resetting buffer queues, display flags, ring pointers, and reallocation markers.

## Dependencies and Integration
The frontend depends on V4L2 mem2mem, vb2 DMA-contig buffers, runtime PM, Wave5 helper functions, `wave5-vpuapi` decoder API wrappers, Wave5 hardware backend, SRAM/VDI allocation, and platform registration in `wave5-vpu.c`. It integrates with userspace through ioctls, events (`V4L2_EVENT_EOS`, `V4L2_EVENT_SOURCE_CHANGE`), and standard stateful decoder semantics.

## Risks and Test Signals
Risks include complex state transitions under streamoff, EOS, queueing failure, dynamic resolution change, and IRQ completion; ring-buffer wrap accounting; minimum capture buffer enforcement; bitdepth/product restrictions; lock ordering between spinlocks, mutexes, and mem2mem callbacks; runtime PM balancing; and cleanup while firmware commands are pending. Test signals include v4l2-compliance stateful decoder tests, H264/HEVC decode with DRC, EOS and drain behavior, streamoff on each queue, capture buffer starvation, ring-buffer wrap with multiple source buffers, 10-bit rejection/support paths, queueing-failure retry, open/close races, and lockdep/KASAN runs.
