# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vi.c

## Purpose
Implements the generic Tegra VI host1x client, V4L2 video nodes, vb2 queue operations, ioctl/control handling, async media graph construction, TPG graph setup, runtime PM, and platform probe/remove.

## Important APIs, Types, And Functions
Format lookup helpers map mbus codes/fourccs to SoC format tables. vb2 ops validate buffer size, store DMA addresses, enqueue buffers, and delegate stream start/stop to SoC ops. Public helpers locate remote bridge/source/CSI subdevices, set stream state, release buffers, and cleanup channels. Ioctls cover capability, params, framesizes/intervals, format negotiation, selection, EDID, DV timings, input enumeration, and event subscription. Controls include TPG mode or syncpoint retry plus optional H/V flip. Async graph functions recursively parse fwnode links, bind subdevices, create media links, register video devices, and initialize format bitmaps.

## Control Flow
Probe maps VI registers, gets clock/PM domain, populates child devices, optionally enables SoC VI access, and registers as host1x client. Host1x init allocates channels from TPG or DT graph, initializes video/vb2/media state, stores `vid->vi`, and registers async notifiers. When all graph subdevs bind, the video node is registered, media links are created, controls are attached, formats are initialized, and subdev hostdata is set. Streaming resumes PM and delegates to the SoC backend.

## State And Persistence
Per-channel state includes video/vb2 objects, mutexes/spinlocks, capture/done lists, active format/fmtinfo, sequence, offsets, port mapping, controls, bitmaps, TPG mode, notifier, and flip flags. Channel memory is intentionally `kzalloc`-managed and freed only when V4L2 device release runs, allowing open file descriptors to outlive platform unbind.

## Dependencies And Integration Points
Depends on host1x, V4L2 core, media controller, V4L2 async/fwnode, vb2 DMA-contig, runtime PM, clocks, and SoC ops from `tegra20.c`/`tegra210.c`. Integrates with CSI/VIP subdevices and the top-level `tegra_video_device`.

## Risks And Test Signals
Graph parsing recursively walks endpoints and can skip broken channels; notifier cleanup and delayed channel free are lifetime-sensitive. Format negotiation uses temporary subdev state and fallback crop logic. Test signals include DT graph variants, async bind order, open-unbind-close lifetime, all ioctl paths against sensors/bridges, stream error propagation on source-change events, and vb2 queue release with pending buffers.
