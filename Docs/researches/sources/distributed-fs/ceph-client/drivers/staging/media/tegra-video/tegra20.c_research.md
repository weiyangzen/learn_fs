# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/tegra20.c

## Purpose
Provides Tegra20/Tegra30-specific VI, CSI, MIPI calibration, VIP, register definitions, supported formats, and SoC data for the generic Tegra video driver.

## Important APIs, Types, And Functions
VI helpers map mbus/fourcc formats to Tegra20 register encodings, enable VI through an APB_MISC bit, allocate two host1x syncpoints, align formats to 32..8190 dimensions and 8-pixel stride, compute flip/planar offsets, program buffer addresses, and run a capture kthread. `tegra20_vi_start_streaming()` starts the media pipeline, enables upstream streaming, programs capture registers, and starts capture; stop tears down the thread and releases buffers. MIPI ops program CSI calibration registers and poll for completion. CSI ops clean status, program pixel parser/CIL/VI output, start/stop per port, and support two channels. VIP ops program parallel input registers and syncpoint output. The file exports `tegra20_vi_soc`, `tegra20_csi_soc`, `tegra30_csi_soc`, and `tegra20_vip_soc`.

## Control Flow
Generic VI calls SoC `vi_start_streaming`; this starts the media pipeline and upstream bridge, then the kthread dequeues buffers and captures one frame at a time. CSI stream-on programs port registers before sensor stream-on; each frame waits for frame-start and memory-write syncpoints. VIP streaming is called through the VIP subdev and programs parallel input before upstream streaming.

## State And Persistence
State is in VI channel fields: syncpoints, queue offsets, sequence, kthread pointer, flip flags, and current format. HAL-like register state is volatile and reprogrammed on stream start. No persistent storage.

## Dependencies And Integration Points
Depends on host1x syncpoints, kthreads, Tegra MIPI calibration, V4L2 media bus formats, VI/CSI/VIP generic headers, and platform clocks/PM provided by generic probe. Integrates with `vi.c` vb2 queues and `csi.c` MIPI sequencing.

## Risks And Test Signals
The APB_MISC enable is undocumented and high-risk. Capture currently releases buffers as done even after some timeout paths, which deserves hardware testing. Syncpoint waits use an `-ERESTARTSYS` workaround. Test signals include Tegra20/Tegra30 VIP and CSI capture, YUV/RAW/YUV420 formats, H/V flip offsets, MIPI calibration timeout handling, and stream stop with pending buffers.
