# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/tegra210.c

## Purpose
Provides Tegra210-specific VI/CSI register access, capture sequencing, error recovery, supported formats, TPG programming, clock lists, and SoC data.

## Important APIs, Types, And Functions
VI ops allocate per-gang-port frame-start and MW_ACK syncpoints, align formats to 64-byte surfaces, program VI_CSI image definitions/sizes/surfaces, perform VI soft reset, recover from capture errors, and run start/finish capture kthreads. `tegra210_vi_start_streaming()` configures syncpoint behavior, starts media pipeline and upstream CSI, then launches both kthreads. CSI ops include per-port recover, start, stop, and ganged-port iteration. TPG programming configures pattern mode, blanking, phase, and RGB frequencies. `tegra210_video_formats` maps RAW8/10/12, RGB888, YUV422, and NV16. Exports `tegra210_vi_soc` and `tegra210_csi_soc`.

## Control Flow
For each queued buffer, the start thread programs surfaces for all active gang ports, reserves syncpoint thresholds, writes VI increment conditions, triggers single-shot capture, waits for frame-start thresholds, and queues the buffer to the done list. The finish thread waits for MW_ACK thresholds and completes the vb2 buffer. On frame-start timeout the driver increments syncpoints, clears errors, soft-resets VI, reprograms capture, and asks CSI to recover.

## State And Persistence
Runtime state lives in `tegra_vi_channel`: per-port syncpoints, done/capture lists, MW thresholds stored in each buffer, kthread pointers, sequence, and active ganged-port count. Register state is volatile and rebuilt on stream start/recovery.

## Dependencies And Integration Points
Depends on host1x syncpoints, kthreads, V4L2/vb2 from `vi.c`, CSI channel metadata from `csi.c`, and Tegra210 clocks including optional `csi_tpg`.

## Risks And Test Signals
Ganged x8 capture, syncpoint FIFO overflow behavior, software recovery, and surface offsets are high-risk. TPG-only defaults differ from sensor mode, so both configurations need coverage. Test signals include RAW/YUV/RGB/NV16 capture, 1/2 ganged ports, frame-start and MW_ACK timeout recovery, TPG 720p/1080p/4K framerate reporting, runtime PM balance, and no leaked kthreads on streamoff errors.
