# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vidc.c

## Purpose
Provides the V4L2 file operations, mem2mem queue initialization, ioctl dispatch, session open/close, and ops-table initialization for Iris decoder and encoder video devices.

## Important APIs And Functions
- `iris_v4l2_fh_init()`/`deinit()` manage V4L2 file handles and control handler attachment.
- `iris_add_session()`/`remove_session()` maintain `core->instances` with max-session gating.
- `iris_m2m_queue_init()` initializes OUTPUT and CAPTURE vb2 queues using DMA-contig memory and Iris vb2 ops.
- `iris_open()` identifies decoder vs encoder by video-device name, runtime-resumes and initializes the core, allocates a generation-specific instance, initializes locks/lists/completions/m2m context, calls decoder/encoder instance init, and registers the session.
- `iris_session_close()` sends HFI session close and waits for response.
- `iris_check_num_queued_internal_buffers()` reports internal buffer leaks on close.
- `iris_close()` frees controls, m2m context, firmware session, internal buffers, session list entry, locks, formats, and instance.
- ioctl helpers dispatch enum/try/set/get format, frame sizes, frame intervals, querycap, selection, event subscription, stream parameters, and decoder/encoder commands.
- Static `iris_v4l2_file_ops`, `iris_vb2_ops`, `iris_v4l2_ioctl_ops_dec`, and `iris_v4l2_ioctl_ops_enc` are installed by `iris_init_ops()`.

## Control Flow And Integration Points
`iris_probe.c` calls `iris_init_ops()` then installs the file/ioctl ops into decoder and encoder `video_device`s. Userspace open creates an Iris instance and m2m queues. Generic V4L2 ioctls reach dispatch helpers here, then call decoder/encoder-specific code. vb2 queue callbacks come from `iris_vb2.c`.

## State And Persistence Behavior
Creates per-open `iris_inst` state: session ID, domain, locks, buffer lists, completions, V4L2 fh, m2m device/context, formats, controls, rates, and firmware caps. `iris_close()` tears all of it down and checks for unreleased internal buffers. Core state is initialized on open and shared by sessions.

## Dependencies
Depends on PM runtime, V4L2 ioctl/event/mem2mem, videobuf2 DMA-contig, Iris instance/decoder/encoder/vb2/VPU-buffer/platform definitions, and HFI/core operations.

## Risks
- `iris_add_session()` silently does not add the instance if max-session count is reached, but `iris_open()` still returns success; later queue setup detects missing instance and fails. This is a behavioral risk for userspace.
- Device role detection depends on exact `video_device.name` strings.
- Close order is delicate: m2m context is released before firmware close and buffer destruction while `inst->lock` is later acquired.
- Internal buffer leak checks only log errors; they do not fail close.
- `iris_m2m_device_run()` is empty because firmware work is queue-driven; mem2mem scheduler behavior relies on explicit buffer completion elsewhere.

## Test Signals
- Open/close stress across max session count.
- V4L2 compliance for decoder and encoder device nodes.
- Frame-size/interval enumeration for supported and unsupported formats.
- Leak/error injection in stream-on followed by close should not leave internal buffers.
