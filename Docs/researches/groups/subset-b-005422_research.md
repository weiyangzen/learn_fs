# subset-b-005422 Research

Grouped research for the exact subset B work item. Each section preserves the original source path and is wrapped for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_proc.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_proc.h

## Purpose
Declares the Allwinner A31 `sun6i-isp-proc` V4L2 subdevice, which is the ISP processing node between CSI input, metadata parameter input, and capture output. The header is the shared contract between the proc implementation and the rest of the sun6i ISP driver.

## Important APIs, Types, And Functions
`enum sun6i_isp_proc_pad` fixes the media pad layout: CSI sink, params sink, and source. `struct sun6i_isp_proc_format` maps media-bus codes to hardware input format and YUV sequence values consumed by the register programming path. `struct sun6i_isp_proc_source` tracks an upstream subdevice, parsed fwnode endpoint, and whether it is expected. `struct sun6i_isp_proc_async_subdev` embeds a V4L2 async connection with backpointer to the source. `struct sun6i_isp_proc` owns the V4L2 subdev, pads, async notifier, active mbus format, a format mutex, and two CSI source slots. Exported helpers are `sun6i_isp_proc_dimensions()`, `sun6i_isp_proc_format_find()`, `sun6i_isp_proc_setup()`, and `sun6i_isp_proc_cleanup()`.

## Control Flow
Setup allocates/registers the processing subdevice and async notifier; graph binding fills the `source_csi0/source_csi1` structures; format negotiation updates `mbus_format` under `lock`; dimensions are later consumed by parameter and capture configuration. Cleanup must unregister notifier/subdev resources in reverse.

## State And Persistence
State is in-memory kernel driver state only. The persistent contract is the media graph topology and active mbus format exposed through V4L2 while the device is registered.

## Dependencies And Integration Points
Depends on V4L2 device/subdevice, media pads, V4L2 fwnode endpoint parsing, and the parent `struct sun6i_isp_device`. Integrates with capture, params, and main ISP register programming through format/dimension helpers.

## Risks And Test Signals
Risk centers on async graph binding and format propagation: wrong pad indices or stale `mbus_format` would misprogram hardware dimensions or input format bits. Test signals include media graph enumeration, async notifier bind/unbind, `VIDIOC_SUBDEV_G/S_FMT`, streaming through CSI plus params queue, and cleanup without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_proc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_reg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_reg.h

## Purpose
Defines the Allwinner A31 ISP register offsets, bit fields, and packed value helpers used by the sun6i ISP driver. It is a hardware ABI header for the kernel driver, not a userspace ABI.

## Important APIs, Types, And Functions
`SUN6I_ISP_ADDR_VALUE()` converts DMA addresses to the hardware word-address representation. Frontend macros cover source mode, enable/control, interrupts, register load/save addresses, SRAM access, and table/stat buffers. Module and mode macros enable AE, OBC, DPC, BDNF, AWB/WB, LSC, histogram, scaler/output paths, and source inputs. Format constants encode YUV420/YUV422 and RAW Bayer orders. Later blocks define AE window registers, optical black geometry, BDNF thresholds/coefficients, Bayer offsets/gains, WB gains/clipping, main/sub-channel sizes, scaling ratios, output formats, strides, and plane addresses.

## Control Flow
The header has no executable flow. Runtime code composes register writes from these macros during probe/table setup, params configuration, capture configuration, interrupt handling, and buffer address programming.

## State And Persistence
The macros describe volatile MMIO state. Persistent driver state lives elsewhere; register state is reinitialized on runtime resume, stream start, and parameter updates.

## Dependencies And Integration Points
Depends on Linux `BIT()` and `GENMASK()`. Used by sun6i ISP core, params, capture, and proc code to keep field packing consistent across modules.

## Risks And Test Signals
Incorrect masks or shifts can silently corrupt adjacent hardware fields. Address helpers are sensitive to DMA alignment. Test signals are successful stream start/stop, correct image dimensions/stride/plane addresses, parameter buffer updates affecting Bayer/BDNF/WB behavior, interrupt status clearing, and suspend/resume reconfiguration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/uapi/sun6i-isp-config.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/uapi/sun6i-isp-config.h

## Purpose
Defines the userspace-visible metadata format and configuration payload for Allwinner A31 ISP parameter buffers.

## Important APIs, Types, And Functions
`V4L2_META_FMT_SUN6I_ISP_PARAMS` identifies parameter metadata buffers with fourcc `S6IP`. `SUN6I_ISP_MODULE_BAYER` and `SUN6I_ISP_MODULE_BDNF` are `modules_used` bits. `struct sun6i_isp_params_config_bayer` carries per-channel black offsets and gains for R/Gr/Gb/B. `struct sun6i_isp_params_config_bdnf` carries denoise distance thresholds and green/RB coefficient arrays. `struct sun6i_isp_params_config` combines module selection with both configuration blocks.

## Control Flow
Userspace queues metadata buffers of this format; the params video node validates and copies the structures, then kernel code applies selected blocks to ISP registers during parameter update points.

## State And Persistence
This is a stable uAPI contract. Values persist only as queued/applied buffer contents and active driver parameter state; there is no file-backed persistence.

## Dependencies And Integration Points
Depends on Linux fixed-width uAPI types and V4L2 fourcc definitions. Integrates with the sun6i params queue and the register definitions for Bayer and BDNF fields.

## Risks And Test Signals
Any layout change would break userspace ABI. Risks include missing range validation for coefficients/gains and userspace/kernel disagreement about `modules_used`. Test signals include `VIDIOC_ENUM_FMT` on the metadata node, queueing exact-size parameter buffers, applying only selected modules, and ABI-size checks across 32/64-bit userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/uapi/sun6i-isp-config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/Kconfig

## Purpose
Adds configuration entries for the NVIDIA Tegra host1x VI/CSI video input staging driver and optional Tegra210 test pattern generator mode.

## Important APIs, Types, And Functions
`VIDEO_TEGRA` is a tristate depending on `TEGRA_HOST1X` and `VIDEO_DEV`, selecting `MEDIA_CONTROLLER`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_FWNODE`. `VIDEO_TEGRA_TPG` is a bool depending on `VIDEO_TEGRA` and `ARCH_TEGRA_210_SOC`.

## Control Flow
Kconfig selection controls whether `tegra-video.ko` is built and whether TPG-only graph setup paths are compiled/enabled.

## State And Persistence
No runtime state. It persists as kernel configuration.

## Dependencies And Integration Points
Integrates with host1x, V4L2, media controller, vb2 DMA-contig, and SoC-specific build symbols.

## Risks And Test Signals
Missing selects cause link or runtime registration failures; overly broad TPG enablement would expose unsupported SoCs. Test signals are `olddefconfig`, module build for Tegra20/Tegra30/Tegra210, and runtime graph creation with and without TPG.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/Makefile

## Purpose
Defines the object composition for the Tegra staging video input module.

## Important APIs, Types, And Functions
`tegra-video-objs` always includes `video.o`, `vi.o`, `vip.o`, and `csi.o`. SoC-specific objects add `tegra20.o` for Tegra2x/3x and `tegra210.o` for Tegra210. `obj-$(CONFIG_VIDEO_TEGRA)` links the module.

## Control Flow
The build graph determines which exported SoC data symbols exist for `of_match_table` entries in VI/CSI/VIP probe paths.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Integrates with Kconfig architecture symbols and the platform drivers declared in `video.h`.

## Risks And Test Signals
Mismatched object inclusion can leave compatible table references unresolved or omit SoC ops. Test signals are per-architecture builds and module load symbol resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/csi.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/csi.c

## Purpose
Implements the Tegra CSI host1x client and V4L2 subdevice layer, including endpoint parsing, TPG pad operations, runtime power, MIPI calibration sequencing, CSI stream-on/off, and channel lifecycle.

## Important APIs, Types, And Functions
TPG-only pad ops include `csi_enum_bus_code()`, `csi_enum_framesizes()`, `csi_enum_frameintervals()`, `csi_get_format()`, `csi_set_format()`, and `tegra_csi_get_frame_interval()`. `tegra_csi_calc_settle_time()` derives D-PHY settle timings from CIL clock and source pixel rate. `tegra_csi_enable_stream()` powers CSI, enables/calibrates MIPI pads, starts CSI hardware, then starts the source subdev for real sensors. `tegra_csi_disable_stream()` reverses source, hardware, MIPI, and runtime PM. Channel allocation/init functions parse DT graph channels and lane counts or synthesize TPG channels. Probe maps registers, gets clocks/regulator, adds optional MIPI provider ops, enables PM runtime, and registers as host1x client.

## Control Flow
Platform probe prepares resources and host1x registration. Host1x init allocates CSI channels, initializes subdevices, and stores `vid->csi`. On stream-on, VI calls the CSI subdev `s_stream`; CSI resumes PM, handles MIPI calibration around sensor stream-on, delegates hardware programming to SoC ops, and unwinds on error. Error recovery stops CSI, calls SoC recovery, and restarts.

## State And Persistence
Runtime state lives in `struct tegra_csi` and per-channel `struct tegra_csi_channel`: active format, blanking/framerate, pixel rate, MIPI handle, lane/gang-port mapping, and list membership. No persistent storage.

## Dependencies And Integration Points
Depends on host1x, runtime PM, clock bulk APIs, regulator `avdd-dsi-csi`, Tegra MIPI calibration, V4L2 fwnode/async/media, and SoC ops from `tegra20.c` or `tegra210.c`. Integrates with VI via subdev hostdata and `tegra_channel_get_remote_*` helpers.

## Risks And Test Signals
Lane validation, ganged-port mapping, PM unwind, and MIPI calibration ordering are high-risk. `csi_set_format()` uses nearest-size logic for TPG and should be checked for width/height argument correctness. Test signals include DT graph parsing, 2-lane/4-lane/ganged stream start, TPG format/framerate enumeration, MIPI calibration success/failure, runtime PM refcount balance, and recovery after CSI errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/csi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/csi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/csi.h

## Purpose
Declares the Tegra CSI data model, constants, SoC operation table, and cross-module helpers.

## Important APIs, Types, And Functions
Constants describe CSI bricks, lane counts, ganged ports, and pad count. `struct tegra_csi_channel` owns the V4L2 subdev, pads, DT node, gang/lane mapping, TPG mode, active mbus format, blanking/framerate, MIPI handle, and pixel rate. `struct tpg_framerate` maps TPG resolution/format to blanking and framerate. `struct tegra_csi_ops` provides SoC callbacks for start, stop, and error recovery. `struct tegra_csi_soc` carries ops, MIPI ops, channel count, clocks, and TPG table. `struct tegra_csi` is the device-level host1x client with iomem, clocks, regulator, ops, lock, and channel list. Exports include `tegra_csi_error_recover()` and `tegra_csi_calc_settle_time()`.

## Control Flow
The header enables generic `csi.c` to operate through SoC callbacks supplied by `tegra20.c`/`tegra210.c` while VI locates CSI subdevices and calls stream operations.

## State And Persistence
All state is runtime kernel memory. Format and TPG settings persist for the life of a channel or until changed by pad ops/control flow.

## Dependencies And Integration Points
Depends on media entity, V4L2 async/subdev, host1x, clocks, regulators, and Tegra MIPI calibration types. Used by VI, CSI, and SoC backend files.

## Risks And Test Signals
Struct layout and constants define assumptions for all backends. Risks include port array bounds for ganged channels and optional callback handling. Test signals are compile coverage for all enabled SoC symbols and runtime stream coverage with TPG and external sensors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/csi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/tegra20.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/tegra20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/tegra210.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/tegra210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vi.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vi.h

## Purpose
Declares the generic Tegra VI data model, SoC operation interface, channel/buffer structures, image data types, video format descriptors, controls, and cross-module helpers.

## Important APIs, Types, And Functions
`V4L2_CID_TEGRA_SYNCPT_TIMEOUT_RETRY` is a private camera-class control. `struct tegra_vi_ops` abstracts SoC-specific enable, syncpoint, format alignment, queue setup, and stream start/stop. `struct tegra_vi_soc` carries format tables, default format, ops, hardware revision, channel/clock limits, and H/V flip support. `struct tegra_vi_channel` owns the video device, vb2 queue, locks, syncpoints, capture kthreads, active format, offsets, buffer lists, port mapping, controls, format bitmaps, TPG mode, notifier, and flip flags. `struct tegra_channel_buffer` extends vb2 with DMA address and MW_ACK thresholds. `struct tegra_video_format` maps CSI data type/bit width/mbus code/bpp/hardware image format/fourcc.

## Control Flow
This header lets `vi.c` implement common V4L2 behavior while backend files install SoC ops and format tables. CSI and VIP code use helper declarations to find remote subdevices and control streaming.

## State And Persistence
All state is runtime kernel memory tied to channel/video-device lifetimes. Active V4L2 state is visible through ioctls while the node exists.

## Dependencies And Integration Points
Depends on host1x, V4L2, media entity, vb2, controls, waitqueues, spinlocks, and `csi.h`. Used across all Tegra video source files.

## Risks And Test Signals
The structure aggregates many lifetime domains, so cleanup ordering and lock usage matter. Port arrays are bounded by `GANG_PORTS_MAX`. Test signals are compile coverage across SoCs, control registration, ganged capture, and stream start/stop with concurrent queue operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/video.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/video.c

## Purpose
Implements the top-level `tegra-video` host1x driver and module init/exit that bind VI, CSI, and VIP platform clients into one V4L2/media device.

## Important APIs, Types, And Functions
`tegra_v4l2_dev_release()` cleans VI channels, unregisters V4L2/media devices, and frees the aggregate device. `tegra_v4l2_dev_notify()` forwards V4L2 subdev events to the video node and marks the vb2 queue errored on source changes during streaming. `host1x_video_probe()` allocates `tegra_video_device`, initializes/registers media and V4L2 devices, calls `host1x_device_init()`, and optionally creates TPG nodes. `host1x_video_remove()` tears down TPG, exits host1x, and drops the V4L2 device ref. Module init registers host1x and platform drivers for CSI/VIP/VI.

## Control Flow
Module load registers the aggregate host1x driver first, then platform drivers. Host1x probe creates media/V4L2 roots before child clients initialize. Remove unregisters child/platform state via host1x exit, with final channel cleanup deferred to V4L2 release.

## State And Persistence
Owns the aggregate `tegra_video_device` lifetime and stores it as host device driver data. No persistent storage.

## Dependencies And Integration Points
Depends on host1x core, platform driver registration, V4L2 device/media device APIs, and platform drivers declared in `video.h`.

## Risks And Test Signals
Registration unwind paths must avoid leaks and double cleanup, especially with TPG setup failure. Event forwarding assumes subdev hostdata points to a valid VI channel. Test signals include module load/unload, probe failure injection at media/V4L2/host1x/TPG stages, source-change event delivery, and open file descriptors across device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/video.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/video.h

## Purpose
Declares the aggregate Tegra video device shared by top-level host1x, VI, CSI, and VIP modules.

## Important APIs, Types, And Functions
`struct tegra_video_device` contains the root `v4l2_device`, `media_device`, and pointers to initialized VI and CSI clients. It declares TPG node setup/cleanup and extern platform drivers `tegra_vi_driver`, `tegra_vip_driver`, and `tegra_csi_driver`.

## Control Flow
`video.c` creates the aggregate object; VI and CSI host1x init store their pointers into it; TPG setup consumes both pointers to create links and nodes.

## State And Persistence
Runtime-only aggregate state. Lifetime is tied to the V4L2 device release path.

## Dependencies And Integration Points
Depends on host1x, media device, V4L2 device, and `vi.h`. Included by top-level, VI, CSI, and VIP files.

## Risks And Test Signals
Pointers may be temporarily NULL depending on host1x child init ordering; TPG setup explicitly checks this. Test signals are host1x child ordering, TPG setup, and removal ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/video.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vip.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vip.c

## Purpose
Implements the Tegra VIP parallel video bridge as a host1x client and V4L2 subdevice.

## Important APIs, Types, And Functions
Inline helpers convert host1x client/subdev/channel pointers. `tegra_vip_channel_get_prev_subdev()` finds the upstream subdevice connected to the VIP sink pad. Stream ops resume runtime PM, call SoC `vip_start_streaming()`, and then start the previous subdev; stream-off calls previous subdev stop and drops PM. DT parsing requires a parallel bus endpoint and exactly two pads. Channel init registers a media bridge subdev. Probe creates `struct tegra_vip`, attaches SoC data, registers as host1x client, and enables runtime PM.

## Control Flow
Platform probe registers the host1x client. Host1x init parses the VIP node and registers the subdevice. VI graph completion links VIP between upstream source and VI video node. During VI stream-on, VIP programs hardware and starts upstream streaming.

## State And Persistence
Runtime state is one `tegra_vip_channel` with subdev, pads, and DT node, plus device-level SoC/client pointers. No persistent storage.

## Dependencies And Integration Points
Depends on V4L2 fwnode/media/subdev, OF graph, runtime PM, host1x, and Tegra20 VIP SoC ops. Integrates with VI through media links and subdev hostdata set by graph completion.

## Risks And Test Signals
`prev_subdev` is assumed present in stream paths; malformed graphs can cause failures. Runtime PM is enabled after host1x registration in probe, so ordering should be checked. Test signals include parallel endpoint parsing, media link creation, stream-on/off with upstream decoder, and probe/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vip.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vip.h

## Purpose
Declares the Tegra VIP parallel-input bridge structures and SoC operation interface.

## Important APIs, Types, And Functions
Pad constants define sink/source layout. `struct tegra_vip_channel` owns the subdev, two media pads, and DT node. `struct tegra_vip_ops` currently has `vip_start_streaming()`. `struct tegra_vip_soc` wraps ops. `struct tegra_vip` owns device, host1x client, SoC data, and the single channel. Tegra20/Tegra30 builds export `tegra20_vip_soc`.

## Control Flow
The generic VIP implementation calls SoC start-streaming through this interface while VI controls the overall pipeline.

## State And Persistence
Runtime-only state; media graph registration persists only while the device is bound.

## Dependencies And Integration Points
Depends on V4L2 async/subdev and media entities. Integrated by `vip.c`, `tegra20.c`, and top-level platform driver registration.

## Risks And Test Signals
The current ops interface lacks stop/error callbacks, so any hardware needing explicit disable would need extension. Test signals include compile coverage for non-Tegra20 builds and stream cycles on VIP hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/tegra-video/vip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/most/Kconfig

## Purpose
Defines the staging MOST components menu and includes component-specific Kconfig files.

## Important APIs, Types, And Functions
`MOST_COMPONENTS` is a tristate requiring `HAS_DMA`, `CONFIGFS_FS`, and `MOST`. It describes the core module name `most_core` and sources `net`, `video`, and `dim2` Kconfig files when enabled.

## Control Flow
Controls whether MOST component drivers are visible/selectable in kernel configuration.

## State And Persistence
No runtime state; persists as kernel config.

## Dependencies And Integration Points
Integrates with the MOST core framework, configfs, DMA support, and child component Kconfigs.

## Risks And Test Signals
Dependency mismatches can expose modules without required core support. Test signals are menuconfig visibility and builds with individual child components enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/most/Makefile

## Purpose
Routes enabled MOST component builds into their subdirectories.

## Important APIs, Types, And Functions
Adds `net/`, `video/`, and `dim2/` directories based on `CONFIG_MOST_NET`, `CONFIG_MOST_VIDEO`, and `CONFIG_MOST_DIM2`.

## Control Flow
Build-time only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Works with child Kconfig symbols and subdirectory Makefiles.

## Risks And Test Signals
Incorrect object routing would omit selected modules. Test signal is an allmodconfig or targeted staging MOST build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/Kconfig

## Purpose
Adds configuration for the MOST DIM2 MediaLB hardware dependent module.

## Important APIs, Types, And Functions
`MOST_DIM2` is a tristate named `DIM2`, depending on `HAS_IOMEM` and `OF`. Help text states it connects via MediaLB to a network transceiver and builds module `most_dim2`.

## Control Flow
Build-time selection controls whether the DIM2 platform driver and HAL are compiled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Requires MMIO and device-tree support, and is included under `MOST_COMPONENTS`.

## Risks And Test Signals
The driver also uses DMA, interrupts, clocks, and MOST core APIs via parent dependencies. Test signals are DT-based build coverage and module probe with supported compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/Makefile

## Purpose
Defines the build recipe for the DIM2 MOST module.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MOST_DIM2)` builds `most_dim2.o`, composed from `dim2.o` and `hal.o`.

## Control Flow
Build-time only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Ties the platform/MOST interface layer to the DIM2 HAL implementation.

## Risks And Test Signals
Both objects are required; omitting `hal.o` would leave DIM API symbols unresolved. Test signal is a targeted `M=drivers/staging/most/dim2` build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/dim2.c -->
# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/dim2.c

## Purpose
Implements the MOST HDM for DIM2/MediaLB hardware: platform probe, MOST interface registration, channel configuration, DMA buffer enqueue/completion, interrupt handling, network-info delivery, sysfs lock state, and platform-specific clock/PHY enablement.

## Important APIs, Types, And Functions
`struct hdm_channel` tracks per-channel MOST/HAL state, pending and started MBO lists, direction, type, and reset DBR pointer. `struct dim2_hdm` owns 31 DMA channels, MOST interface/capabilities, MMIO base, clocks, netinfo thread/waitqueue, MAC/link state, async-TX index, and platform hooks. `configure_channel()` normalizes buffer sizes and initializes HAL channels by MOST data type. `enqueue()` adds MBOs to pending and tries transfer. `poison_channel()` destroys HAL channel and completes pending/started MBOs with close status. IRQ paths call `dim_service_mlb_int_irq()`, `dim_service_ahb_int_irq()`, `dim_service_channel()`, `service_done_flag()`, and `try_start_dim_transfer()`. Probe parses `microchip,clock-speed`, maps MMIO, starts HAL, requests interrupts, starts netinfo thread, fills capabilities, and registers MOST interface.

## Control Flow
Userspace/MOST core configures a channel, then enqueues MBOs. Pending MBOs move to started when HAL reports ready and DBR space exists. AHB IRQ top half services HAL interrupt state and wakes threaded handler; threaded handler services each channel, detaches completed buffers, completes MBOs, and starts more transfers. Async RX network-info packets are parsed and recycled; a thread calls the MOST netinfo callback.

## State And Persistence
State is runtime-only. The driver keeps MBO queues under `dim_lock`, active HAL channel state, DBR sizing, async-TX index, link/MAC info, and platform clock handles. Sysfs `state` exposes MediaLB lock status.

## Dependencies And Integration Points
Depends on Linux platform/OF/IRQ/clock/DMA/kthread APIs, MOST core (`struct most_interface`, MBO callbacks), and the local HAL. Platform data supports i.MX6, Renesas Gen2/Gen3, and Xilinx compatibles.

## Risks And Test Signals
Global `dim_lock` serializes HAL and list state; completion callbacks are invoked after dropping it, which is important. Busy `while (!try_start_dim_transfer())` loops can spin if progress is rapid. Probe returns directly from `most_register_interface()` after creating a release-managed device, so failure behavior should be checked. Test signals include channel configure/enqueue/poison for all data types/directions, DBR exhaustion, netinfo packet parsing, IRQ storm/empty-list hard error paths, sysfs lock state, and platform clock enable/disable on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/dim2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/errors.h -->
# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/errors.h

## Purpose
Defines HAL error codes for DIM2 initialization, configuration, buffer, underflow, and overflow failures.

## Important APIs, Types, And Functions
`enum dim_errors_t` includes `DIM_NO_ERROR`, init errors for base address, MediaLB clock, channel address, out-of-memory, runtime not-initialized, bad config, bad buffer size, underflow, and overflow.

## Control Flow
HAL functions return these values or pass them to `dimcb_on_error()`; `dim2.c` maps nonzero init/config results to Linux errors and logs them.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by `hal.c`, `hal.h` API callers, and `dim2.c` error reporting.

## Risks And Test Signals
Error values are part of the internal driver/HAL contract. Test signals include forcing bad clock, invalid channel address, oversized DBR allocation, invalid sync/isoc packet sizes, and enqueue overflow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/errors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/hal.c -->
# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/hal.c

## Purpose
Implements the low-level DIM2 hardware abstraction for MediaLB control table programming, DBR memory allocation, channel setup/teardown, buffer start/detach, interrupt servicing, MediaLB lock detection, and buffer-size normalization.

## Important APIs, Types, And Functions
Global `g` stores initialization state, MMIO base, fcnt, DBR allocation bitmap, and async-TX DBR accounting. DBR helpers allocate/free 16 KiB internal buffer RAM in fixed blocks. CTR helpers write/read CDT, ADT, MLB CAT, and AHB CAT entries through MADR/MDAT/MDWE. `dim2_configure_channel()` programs CDT/CAT/ADT and unmasks channel interrupts; `dim2_clear_channel()` reverses it. Async-TX DBR accounting tracks read/write pointer movement and remaining space. `dim_startup()`, `dim_shutdown()`, `dim_init_control()`, `dim_init_async()`, `dim_init_isoc()`, `dim_init_sync()`, `dim_destroy_channel()`, `dim_service_*()`, `dim_get_channel_state()`, `dim_enqueue_buffer()`, and `dim_detach_buffers()` form the exported HAL.

## Control Flow
Startup validates MMIO/clock/fcnt, clears hardware, configures MediaLB/HBI/DMA, and marks initialized. Channel init validates address/type sizes, allocates DBR, initializes software counters, and writes channel tables. Enqueue validates size and two-entry hardware queue depth, writes ADT entries for the next index, updates async DBR accounting, and toggles producer index. IRQ service clears hardware done flags, advances request counters, and task-context service converts requests into software done-buffer counts. Detach decrements done-buffer counts after the upper layer removes MBOs.

## State And Persistence
All state is volatile in static global `g` and `struct dim_channel`. Hardware table/register state is reset on startup/shutdown and channel destroy. No persistent storage.

## Dependencies And Integration Points
Depends on MMIO accessors, local register/error definitions, and the external `dimcb_on_error()` callback supplied by `dim2.c`. The caller must serialize access; `dim2.c` does this with `dim_lock`.

## Risks And Test Signals
The HAL uses a single static global, so only one DIM2 instance is safe. `dim2_transfer_madr()` busy-waits without timeout. DBR allocation/accounting and two-buffer queue state are high-risk. Test signals include startup/shutdown, concurrent channel init/destroy under lock, DBR allocation/free reuse, async TX DBR space accounting as RPC advances, underflow/overflow error paths, and interrupt service with multiple active channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/hal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/hal.h -->
# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/hal.h

## Purpose
Declares the DIM2 HAL public interface, channel state structures, MediaLB clock values, and callback hook used by the platform driver.

## Important APIs, Types, And Functions
`enum mlb_clk_speed` enumerates 256fs through 8192fs. `struct dim_ch_state` reports readiness and completed-buffer count. `struct int_ch_state` holds request/service counters, producer/consumer indices, and queue level. `struct dim_channel` stores channel address, DBR address/size, packet/sync sizing, and done-buffer count. Public APIs cover startup/shutdown, lock state, buffer-size normalization, channel init/destroy for control/async/isoc/sync, MLB/AHB IRQ service, per-channel service, state query, DBR space, enqueue, detach, and error callback.

## Control Flow
`dim2.c` calls startup at probe, init functions during MOST configure, enqueue/detach during buffer flow, service functions from IRQ handlers, and shutdown from release.

## State And Persistence
The header exposes runtime state containers only. Persistent behavior is none.

## Dependencies And Integration Points
Depends on Linux types and `reg.h`. Integrates `dim2.c` with `hal.c`.

## Risks And Test Signals
The API assumes external locking and valid channel lifetimes. Test signals include all init variants, invalid parameters, ready/done state transitions, and no use after `dim_destroy_channel()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/reg.h -->
# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/reg.h

## Purpose
Defines the DIM2/OS62420 MMIO register layout and bit-field constants used by the HAL.

## Important APIs, Types, And Functions
`struct dim2_regs` maps MediaLB, HBI, data transfer, and AHB control/status registers with reserved gaps. `DIM2_MASK()` builds low-bit masks. Enum constants define MLBC0 clock/lock/enable/fcnt fields, MIEN interrupt bits, MLBC1 error/NDA fields, ACTL/HCTL fields, CDT buffer/read-pointer fields, ADT control/status/address fields, and CAT channel table fields for type, enable, read/write, and channel label.

## Control Flow
No executable flow. `hal.c` uses the layout and constants for all MMIO and control table programming.

## State And Persistence
Describes volatile hardware state only.

## Dependencies And Integration Points
Depends on Linux integer types. Included by `hal.h` and `hal.c`.

## Risks And Test Signals
Register layout mismatches cause all HAL behavior to fail. Test signals are MMIO smoke tests on supported hardware, lock-state reads, channel table programming, interrupt mask/status behavior, and DMA transfer completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/sysfs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/sysfs.h

## Purpose
Declares a minimal MediaLB bus wrapper for DIM2 sysfs-related state.

## Important APIs, Types, And Functions
`struct medialb_bus` contains `struct kobject kobj_group`. In this source subset, `dim2.c` defines a `state` device attribute separately and includes this type in `struct dim2_hdm`.

## Control Flow
No functions or executable flow in the header.

## State And Persistence
Only declares a runtime kobject holder. No persistent storage.

## Dependencies And Integration Points
Depends on Linux kobject definitions and is included by `dim2.c`.

## Risks And Test Signals
The type is currently underused in the visible code, so future sysfs expansion must manage kobject initialization/lifetime carefully. Test signals are sysfs attribute registration/removal and probe/remove leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/dim2/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/net/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/most/net/Kconfig

## Purpose
Adds configuration for the MOST networking component.

## Important APIs, Types, And Functions
`MOST_NET` is a tristate named `Net`, depends on `NET`, and builds module `most_net`.

## Control Flow
Build-time selection only.

## State And Persistence
No runtime state in this file.

## Dependencies And Integration Points
Requires the Linux networking stack and is included under `MOST_COMPONENTS`.

## Risks And Test Signals
The help text has a typo but no behavioral effect. Test signals are config visibility and module build with MOST core plus networking enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/net/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/net/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/most/net/Makefile

## Purpose
Defines the build recipe for the MOST networking module.

## Important APIs, Types, And Functions
`obj-$(CONFIG_MOST_NET)` builds `most_net.o`; `most_net-objs` contains `net.o`.

## Control Flow
Build-time only.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Connects `MOST_NET` Kconfig to the networking component implementation.

## Risks And Test Signals
Object naming must match module expectations. Test signal is a targeted build and module load with MOST core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/most/net/Makefile -->
