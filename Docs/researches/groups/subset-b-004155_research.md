# subset-b-004155 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-csi2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-csi2.c

## Purpose
`rcar-csi2.c` is the Renesas R-Car MIPI CSI-2 receiver V4L2 subdevice driver. It receives one CSI-2 input from an upstream sensor/bridge, configures SoC-specific D-PHY or C-PHY hardware, and exposes one or more source pads to downstream VIN or ISP blocks. Gen3 variants generally route virtual channels directly to VIN output channels, while newer ISP-oriented variants expose one source pad and leave per-channel fanout to the ISP/VIN graph.

## Important APIs, Types, And Functions
The central state object is `struct rcar_csi2`, holding device resources, `v4l2_subdev`, pads, async notifier, remote subdevice, lane configuration, C-PHY line order, virtual-channel routing, and `stream_count`. `struct rcar_csi2_info` is the SoC capability table: register layout, PHTW initialization hook, post-PHY hook, receiver-start hook, standby hook, hsfreq tables, number of channels, `use_isp`, and D-PHY/C-PHY support flags. `struct rcar_csi2_format` maps media bus codes to MIPI CSI-2 data types and bits per pixel.

Key entry points are `rcsi2_probe()`, `rcsi2_remove()`, `rcsi2_enable_streams()`, `rcsi2_disable_streams()`, `rcsi2_set_pad_format()`, `rcsi2_irq()`, and `rcsi2_irq_thread()`. Hardware helpers include `rcsi2_start_receiver_gen3()`, `rcsi2_start_receiver_v4h()`, `rcsi2_start_receiver_v4m()`, PHTW writers, `rcsi2_calc_mbps()`, `rcsi2_get_active_lanes()`, and PHY wait/calibration routines.

## Control Flow
Probe allocates private state, selects the matching `rcar_csi2_info` from DT and optionally an H3 ES2 soc revision override, maps registers, requests a threaded IRQ, gets reset control, parses endpoint/lane properties, registers an async notifier for the upstream source, initializes media pads, enables runtime PM, finalizes state, and registers the subdevice. Async bound handling finds the upstream source pad and creates an immutable enabled link into CSI-2 sink pad 0.

Streaming starts through pad `.enable_streams`. The first stream increments from zero via `rcsi2_start()`: runtime PM resumes, reset deasserts, the SoC-specific receiver routine configures VCDT/field detection/lane swap/PHY PLL/PHTW/PHY mode, waits for stop state or calibration, then enables upstream streaming. Stop asserts reset, enters standby, and disables upstream streaming. `stream_count` lets multiple downstream source pads share one physical receiver. Link setup for VIN mode maps enabled source pad links to `channel_vc[]`, enforcing one downstream route per VC.

## State And Persistence
Persistent runtime state is in memory only: active remote pointer/pad, lane count and swaps from fwnode, C-PHY mode/line order, virtual-channel to output-channel mapping, and stream count. Hardware state lives in MMIO registers and is reprogrammed on every stream start or IRQ restart. Runtime PM and reset control gate register access and PHY state. No filesystem or NVRAM state exists.

## Dependencies And Integration Points
The driver depends on V4L2 subdev state, media controller links, V4L2 fwnode endpoint parsing, MIPI CSI-2 data type definitions, runtime PM, reset controller, IRQ handling, and SoC match data. It integrates upstream with sensors/bridges that provide link frequency or pixel-rate metadata and downstream with R-Car VIN or R-Car ISP. Correct DT endpoint bus type, lane count, data-lanes order, and optional C-PHY line orders are critical.

## Risks
The PHY setup contains many SoC-specific magic values and timing tables; wrong match data, link frequency, or lane count can fail calibration or silently corrupt capture. `stream_count` has no explicit underflow guard beyond caller correctness. The threaded IRQ restarts receiver on transfer errors while streams are active, so restart ordering and active-state locking are important. Routing depends on downstream video devices carrying valid `renesas,id`. Gen4 C-PHY/D-PHY register sequences are particularly hardware-sensitive.

## Test Signals
Useful validation signals include successful subdevice registration, media graph links, `dev_info` lane count, link-frequency negotiation, stream start/stop on all supported SoCs, virtual-channel routing to VIN nodes, ISP path operation for `use_isp` variants, IRQ error restart behavior, and timeout/error logs from PHTW, LP-11, PHY calibration, or unsupported PHY speed paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-fcp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-fcp.c

## Purpose
`rcar-fcp.c` is a small shared platform driver for Renesas Frame Compression Processor instances used by other media/display blocks. It does not expose a userspace node; it registers FCP devices in a global in-kernel list and exports helper APIs for other drivers to acquire a device reference, runtime-enable the block, and issue a soft reset.

## Important APIs, Types, And Functions
`struct rcar_fcp_device` stores the global list node, `struct device *`, and MMIO base. Exported APIs are `rcar_fcp_get()`, `rcar_fcp_put()`, `rcar_fcp_get_device()`, `rcar_fcp_enable()`, `rcar_fcp_disable()`, and `rcar_fcp_soft_reset()`. Probe/remove maintain `fcp_devices` under `fcp_lock`. `rcar_fcp_soft_reset()` writes `RCAR_FCP_REG_RST_SOFTRST` and polls `RCAR_FCP_REG_STA_ACT` clear with `readl_poll_timeout()`.

## Control Flow
Probe allocates and maps one FCP instance, sets maximum DMA segment size to `UINT_MAX`, enables runtime PM, appends the device to the global list, and stores drvdata. Consumers later call `rcar_fcp_get(np)`, which searches by DT node and returns a referenced device or `-EPROBE_DEFER` if not registered. Enable/disable are thin wrappers over runtime PM reference counting. Remove deletes the list entry and disables runtime PM.

## State And Persistence
State is limited to the process-lifetime global device list and runtime PM reference count. The driver writes only FCP reset/status registers. There is no userspace state, persistent config, or long-lived buffer ownership.

## Dependencies And Integration Points
The file depends on platform resources, OF matching for `renesas,fcpf` and `renesas,fcpv`, runtime PM, DMA mapping configuration, and exported media header declarations from `<media/rcar-fcp.h>`. It is an integration service for other R-Car multimedia drivers that need an FCP memory path.

## Risks
The global singleton-style list requires consumers to handle `-EPROBE_DEFER`. Runtime PM references must be balanced by consumers. Soft reset assumes the status register's active bit clears within 100 microseconds; hardware stuck active produces an error. Since `rcar_fcp_put()` tolerates NULL, consumers may hide missing optional FCP usage if they fail to check `ERR_PTR` results correctly.

## Test Signals
Check probe for both compatible strings, deferred acquisition before probe, balanced enable/disable PM counts, successful soft reset polling, and consumer-driver behavior when `rcar_fcp_get()` returns `-EPROBE_DEFER`. Removal should delete list membership without dangling references for properly balanced consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-fcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_VIDEO_RCAR_ISP`, the build option for the Renesas R-Car Image Signal Processor Channel Selector driver under `rcar-isp/`.

## Important APIs, Types, And Functions
No C APIs are implemented here. The important symbols are `VIDEO_RCAR_ISP`, its tristate prompt, dependency clauses, and selected subsystem options: `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `RESET_CONTROLLER`, and `V4L2_FWNODE`.

## Control Flow
When enabled as built-in or module, the Kbuild rule in the adjacent Makefile builds `rcar-isp.o` from `csisp.o`. The dependency chain requires V4L platform drivers, OF, video device support, and either Renesas architecture or compile-test coverage.

## State And Persistence
The file has no runtime state. It controls kernel configuration and therefore whether the driver is compiled.

## Dependencies And Integration Points
The dependencies mirror `csisp.c`: media-controller graph support, subdev pad APIs, reset control, and fwnode endpoint parsing. The module name documented in help text is `rcar-isp`.

## Risks
Missing selected dependencies would break compilation or probe-time integration. The option is guarded by `ARCH_RENESAS || COMPILE_TEST`, so non-Renesas runtime availability is intentionally limited unless compile testing.

## Test Signals
Useful checks are `make menuconfig` visibility, compile as `y` and `m`, module name correctness, and build coverage with `COMPILE_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/Makefile

## Purpose
This Makefile builds the R-Car ISP Channel Selector driver.

## Important APIs, Types, And Functions
It declares `rcar-isp-objs = csisp.o` and adds `rcar-isp.o` to `obj-*` when `CONFIG_VIDEO_RCAR_ISP` is enabled.

## Control Flow
Kbuild compiles `csisp.c` into the composite object `rcar-isp.o`. If the config is modular, the resulting module is `rcar-isp.ko`; if built-in, it is linked into the kernel image.

## State And Persistence
No runtime state is present. The file only affects build graph composition.

## Dependencies And Integration Points
It integrates with the Kconfig symbol in the same directory and the kernel media platform build tree.

## Risks
Because only `csisp.o` is listed, future split files must be added here or they will not build. A mismatch between Kconfig help text and object name would confuse module loading, but currently they align.

## Test Signals
Build `CONFIG_VIDEO_RCAR_ISP=y` and `m`, verify `csisp.o` is included once, and confirm `modinfo rcar-isp.ko` when modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/csisp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/csisp.c

## Purpose
`csisp.c` implements the Renesas R-Car ISP Channel Selector as a V4L2 subdevice. The comments state the hardware can do more ISP work, but this driver only selects/filter-routes CSI-2 data types and virtual channels between a CSI-2 receiver and up to eight downstream VIN outputs.

## Important APIs, Types, And Functions
`struct rcar_isp` stores device resources, reset control, selected CSI input, `v4l2_subdev`, nine media pads, async notifier, remote source, and stream count. `struct rcar_isp_format` maps media bus codes to MIPI CSI-2 datatype and ISP processing mode. Important functions are `risp_probe()`, `risp_parse_dt()`, `risp_notify_bound()`, `risp_start()`, `risp_stop()`, `risp_enable_streams()`, `risp_disable_streams()`, and `risp_set_pad_format()`.

## Control Flow
Probe maps the channel selector register block, gets reset control, enables runtime PM, parses one of two possible sink endpoints, initializes a subdevice named `rcar-isp <dev>`, creates one sink pad plus eight source pads, finalizes subdev state, and registers it asynchronously. Binding creates an immutable enabled link from the upstream source pad to ISP sink pad 0.

Streaming starts on the first enabled source stream. `risp_start()` validates the sink pad format, resumes runtime PM, deasserts reset, selects CSI input 0 or 1, configures filter channels 4-7 so each virtual channel accepts the chosen datatype, writes the processing mode for all four VCs for that datatype, starts the ISP, then enables upstream streams. `risp_stop()` disables upstream streams, writes stop, asserts reset, and drops runtime PM. Pad format setting validates against the static table and propagates the sink format to all source pads.

## State And Persistence
Runtime state is the selected input endpoint, remote subdevice pointer/pad, active media bus format in subdev state, and `stream_count`. Register state is re-created on each stream start. There is no persistent storage. Reset and runtime PM define the hardware lifetime.

## Dependencies And Integration Points
The driver depends on platform MMIO, reset control, runtime PM, media controller, V4L2 subdev streams, async notifier/fwnode graph APIs, and MIPI CSI-2 datatype definitions. It integrates upstream with `rcar-csi2.c` on Gen4 ISP paths and downstream with `rcar-vin` in `use_isp` configurations, where VIN creates immutable links from ISP source pads to VIN nodes.

## Risks
Only one stream mask (`BIT_ULL(0)`) is accepted even though eight source pads exist, so callers must use the expected single-stream model. The format table encodes processing modes as hardware constants; incorrect datatype/procmode mapping can break capture. `stream_count` lacks explicit underflow protection. Endpoint parsing accepts the first existing endpoint among IDs 0 and 1, so DT mistakes can select the wrong CSI input. Advanced ISP functions are intentionally unsupported.

## Test Signals
Validate probe for old and generic compatibles, endpoint ID 0/1 selection, subdev node registration, immutable upstream link creation, format propagation to all pads, stream count behavior when multiple VIN links are active, correct CSI datatype filtering for RGB/YUV/RAW8/RAW10/RAW12, runtime PM/reset sequencing, and error paths when no remote or unsupported format is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-isp/csisp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/Kconfig

## Purpose
This Kconfig entry defines `CONFIG_VIDEO_RCAR_VIN`, the Renesas R-Car Video Input capture driver option.

## Important APIs, Types, And Functions
There are no C functions here. Key build semantics are the tristate symbol, prompt, dependency clauses, and selected support libraries: `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_FWNODE`.

## Control Flow
If selected, Kbuild compiles the VIN composite object from `rcar-core.o`, `rcar-dma.o`, and `rcar-v4l2.o`. The help text states the module name is `rcar-vin`.

## State And Persistence
No runtime state exists; this file controls compile-time availability.

## Dependencies And Integration Points
The symbol depends on V4L platform drivers, OF, video device support, and Renesas architecture or compile-test. The selected options match the driver needs for media graph links, subdev APIs, DMA-contiguous vb2 buffers, and fwnode endpoint parsing.

## Risks
Any missing selected dependency would affect build or runtime media integration. Since capture buffers use contiguous DMA memory, omitting `VIDEOBUF2_DMA_CONTIG` would be a hard build break.

## Test Signals
Build with `CONFIG_VIDEO_RCAR_VIN=y` and `m`, confirm object composition and module name, and compile under `COMPILE_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/Makefile

## Purpose
This Makefile builds the R-Car VIN capture driver composite object.

## Important APIs, Types, And Functions
It declares `rcar-vin-objs = rcar-core.o rcar-dma.o rcar-v4l2.o` and links `rcar-vin.o` when `CONFIG_VIDEO_RCAR_VIN` is enabled.

## Control Flow
Kbuild compiles the core platform/media graph file, DMA/vb2 hardware file, and V4L2 ioctl/file-operations file into a single driver object or module.

## State And Persistence
No runtime state exists. The Makefile only controls build composition.

## Dependencies And Integration Points
It integrates the three VIN implementation slices that share declarations from `rcar-vin.h`.

## Risks
Adding new VIN source files without updating this list would omit functionality. Removing one of the three current objects would break exported-internal calls across the driver.

## Test Signals
Build as built-in and module, verify all three objects are linked, and check that exported-internal symbols referenced across the three files resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-core.c

## Purpose
`rcar-core.c` is the platform, media-controller, async-subdevice, SoC-data, routing, controls, and PM core for the Renesas R-Car VIN capture driver. It groups all VIN instances in a system, discovers upstream CSI-2/ISP/parallel sources from DT, creates media links, and registers video nodes once the graph is complete.

## Important APIs, Types, And Functions
The file uses shared types from `rcar-vin.h`: `struct rvin_dev`, `struct rvin_group`, `struct rvin_info`, and `struct rvin_group_route`. Main functions are `rcar_vin_probe()`, `rcar_vin_remove()`, `rvin_group_get()`, `rvin_group_put()`, notifier callbacks, `rvin_csi2_link_notify()`, `rvin_csi2_setup_links()`, `rvin_isp_setup_links()`, `rvin_parallel_setup_links()`, `rvin_create_controls()`, `rvin_suspend()`, and `rvin_resume()`. Static match data describes H1/M1/Gen2/Gen3/Gen4 capabilities, max dimensions, NV12/RAW10 support, routes, and scaler callbacks.

## Control Flow
Probe allocates a VIN, maps registers, gets IRQ, initializes DMA/V4L2 device state through `rvin_dma_register()`, assigns an ID from `renesas,id` for Gen3/Gen4 or IDA for older models, initializes the video entity sink pad, creates alpha controls, and joins a singleton `rvin_group`. Depending on model it initializes ISP links, CSI-2 links, or parallel links, enables runtime PM, and returns. The group notifier waits until all enabled VINs are present, registers async fwnode matches, and on completion registers the media device, subdev nodes, all VIN video nodes, and the graph links.

CSI-2 link notification validates that link changes happen only when no entity is streaming, ensures VINs in a master group attach to one CSI-2 receiver, looks up the proper CHSEL route, writes channel routing via `rvin_set_channel_routing()`, and marks `vin->is_csi`. ISP setup creates immutable enabled links from ISP source pads to VIN nodes based on VIN id. Parallel setup creates direct source-to-VIN links and disables immutable auto-enable if CSI/ISP remotes also exist.

## State And Persistence
Global state is `rvin_group_data`, protected by `rvin_group_lock`, plus `rvin_ida` for legacy IDs. Per-group state includes media device, notifier, VIN array, remote subdev slots, platform info, lock, and refcount. Per-device state includes ID, group membership, controls, `is_csi`, scaler selection, and cached route `chsel` in the DMA file. State is not persistent across driver unload; routing is restored on resume from cached memory.

## Dependencies And Integration Points
This file depends on OF graph parsing, V4L2 async notifiers, media controller, runtime PM, V4L2 controls, and the DMA/V4L2 helper functions defined in sibling files. It integrates with `rcar-csi2`, `rcar-isp`, and parallel sensor/decoder subdevices. Its route tables encode SoC-specific CSI-to-VIN topology.

## Risks
The group allocator assumes only one system-wide VIN group. Link routing is sensitive to `renesas,id` uniqueness and complete DT coverage; duplicate or missing IDs fail probe. Link changes while streaming are blocked, but route state spans multiple VIN instances and master VINs. Error paths after partial notifier/media registration can affect all VIN nodes in the group. Suspend/resume depends on cached CHSEL and master VIN availability.

## Test Signals
Test complete and partial DT groups, duplicate IDs, CSI-2 and ISP graph creation, parallel-only operation, link enable/disable rejection while streaming, route programming for every SoC route table, media device registration only after async completion, alpha control creation, PM suspend/resume while streaming, and clean removal of group/notifier/video nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-dma.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-dma.c

## Purpose
`rcar-dma.c` handles VIN register programming, crop/scale/compose hardware setup, vb2 queue operations, DMA-contiguous capture buffers, IRQ-driven frame completion, stream start/stop, channel routing, and runtime alpha updates.

## Important APIs, Types, And Functions
The private `struct rvin_buffer` wraps `vb2_v4l2_buffer`. Public sibling-file APIs are `rvin_dma_register()`, `rvin_dma_unregister()`, `rvin_start_streaming()`, `rvin_stop_streaming()`, `rvin_set_channel_routing()`, `rvin_set_alpha()`, `rvin_scaler_gen2()`, `rvin_scaler_gen3()`, and `rvin_crop_scale_comp()`. Core internal functions include `rvin_setup()`, `rvin_capture_start()`, `rvin_capture_stop()`, `rvin_irq()`, `rvin_mc_validate_format()`, `rvin_set_stream()`, `rvin_fill_hw_slot()`, and vb2 queue callbacks.

## Control Flow
Registration creates the `v4l2_device`, initializes locks/lists/hardware slots, configures a DMA-contiguous vb2 queue, and requests the VIN IRQ. On vb2 stream start, a scratch buffer is allocated and `rvin_start_streaming()` validates/enables the upstream media pipeline, resets sequence, fills three hardware slots from queued buffers or scratch memory, programs VIN registers, applies crop/scale/compose, and starts continuous capture. IRQ handling acknowledges status, emits frame-sync events on VSYNC, finds the completed hardware slot, timestamps and completes the vb2 buffer if present, increments sequence, and refills the slot. Stop repeatedly disables capture until hardware reports inactive, stops upstream streaming, disables interrupts, returns hardware buffers as error, frees scratch memory, and returns queued buffers.

## State And Persistence
State is in `struct rvin_dev`: active pixel format, crop/compose rectangles, media bus code, queued vb2 list, three hardware slots, scratch buffer DMA address, sequence, running flag, alpha, and cached CHSEL. `qlock` protects buffer/hardware/sequence/running fields. Register state is reprogrammed at stream start and modified dynamically for selection and alpha.

## Dependencies And Integration Points
The file depends on vb2 DMA-contiguous memory, V4L2 events, media pipeline helpers, upstream subdev stream APIs, runtime PM for CHSEL writes, and shared format helpers from `rcar-v4l2.c`. It is called by `rcar-core.c` during probe/remove and by `rcar-v4l2.c` through vb2/file operations.

## Risks
The scratch buffer hides underruns by dropping frames, so tests must watch sequence gaps and debug logs. Hardware buffer addresses must satisfy 128-byte alignment after compose offsets; violations trigger WARN and skipped slot update. Format validation is complex across interlaced/alternate fields, scaling, NV12 alignment, RAW formats, CSI vs parallel input, and Gen3/Gen4 limitations. In `rvin_start_streaming()`, `vin->running` is set after `rvin_capture_start()` even if `rvin_capture_start()` fails after upstream stream enable, so error-path behavior deserves scrutiny. Stop waits bounded retries and logs if hardware stays active.

## Test Signals
Exercise all supported pixel formats, RAW8/RAW10 paths, NV12 channel restrictions, scaling/no-scaling paths, compose offsets, interlaced and alternate fields, buffer underrun with scratch use, IRQ frame completion order, stream start validation failures, streamoff buffer return states, CHSEL writes under runtime PM, and alpha update while streaming for ARGB formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-v4l2.c

## Purpose
`rcar-v4l2.c` implements the VIN userspace-facing V4L2 video node: pixel format enumeration/alignment, selection/crop/compose ioctls, event subscription, file open/release PM handling, video registration, and forwarding notifications from subdevices to the active VIN node.

## Important APIs, Types, And Functions
The static `rvin_formats[]` table maps V4L2 fourcc formats to bytes per pixel. `rvin_format_from_pixel()` is shared with DMA setup and applies SoC/channel restrictions for XBGR32, NV12, and RAW10. Format helpers are `rvin_format_bytesperline()`, `rvin_format_sizeimage()`, and `rvin_format_align()`. IOCTL handlers include querycap, get/try/set format, enum format, get/set selection, and event subscription. File operations are `rvin_open()` and `rvin_release()`. Registration entry points are `rvin_v4l2_register()` and `rvin_v4l2_unregister()`.

## Control Flow
Video registration initializes a `video_device`, sets queue/fops/ioctls/caps, installs a default 800x600 YUYV format, aligns it, registers the node, and stores drvdata. Open resumes runtime PM, opens the V4L2 file handle, powers the media pipeline, and sets up controls. Release delegates streaming cleanup to vb2, drops pipeline PM, unlocks, and runtime-suspends.

Format ioctls force capture colorspace metadata, validate fourcc against VIN capabilities, align width and bytesperline to hardware needs, and reject set-format while vb2 is busy. Selection ioctls expose crop bounds from the remote subdev active format, compose bounds from the active output format, clamp crop/compose rectangles, align compose offsets to hardware buffer-address requirements, update `vin->crop`/`vin->compose`, and call `rvin_crop_scale_comp()` so running hardware can be updated.

## State And Persistence
The active `v4l2_pix_format`, crop rectangle, compose rectangle, and control state are stored in `struct rvin_dev`. These settings persist only while the device is bound. vb2 busy state prevents format changes while buffers are allocated/streaming. Events are queued in the V4L2 framework.

## Dependencies And Integration Points
The file depends on V4L2 ioctl helpers, V4L2 events, media-controller remote pad lookup, runtime PM, pipeline PM, and sibling DMA functions. It integrates with upstream subdevices for crop bounds and notifications and with userspace through `V4L2_CAP_VIDEO_CAPTURE`, streaming, read/write, and media-controller IO capabilities.

## Risks
Selection changes call hardware programming without explicitly checking `running`; this relies on the DMA helper and register accessibility under current PM/open assumptions. Format enumeration has special raw bus-code handling and a TODO for future RAW12. Compose alignment loops decrement top/left until address alignment works, so boundary conditions around zero and format bpp matter. `rvin_remote_rectangle()` depends on an enabled media link and remote `get_fmt`; missing graph setup returns errors to selection ioctls.

## Test Signals
Use `v4l2-ctl --list-formats-ext`, try/set/get format for each SoC capability set, verify bytesperline and sizeimage alignment, test busy `S_FMT`, crop/compose clamping and alignment, frame-sync/source-change event subscription, open/release PM balancing, subdevice event forwarding, and video node removal while graph unbinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-vin.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-vin.h

## Purpose
`rcar-vin.h` is the private shared header for the three VIN implementation files. It defines hardware sizing constants, SoC model enums, CSI/ISP remote IDs, shared format and topology structures, the main VIN device/group state structures, logging macros, and cross-file function prototypes.

## Important APIs, Types, And Functions
Constants include `HW_BUFFER_NUM` (three hardware slots), `HW_BUFFER_MASK` (128-byte alignment mask), `RCAR_VIN_NUM` (32 instances), and `RVIN_REMOTES_MAX`. Important enums are `model_id`, `rvin_csi_id`, and `rvin_isp_id`. Important structs are `rvin_video_format`, `rvin_parallel_entity`, `rvin_group_route`, `rvin_info`, `rvin_dev`, and `rvin_group`. Prototypes connect DMA, V4L2, routing, scaler, alpha, and streaming operations across files.

## Control Flow
No executable control flow is implemented in the header. It defines the contracts used by `rcar-core.c` to allocate/register devices, `rcar-dma.c` to operate hardware and buffers, and `rcar-v4l2.c` to expose userspace operations.

## State And Persistence
`struct rvin_dev` is the key per-device state container: platform resources, V4L2/video/control objects, parallel subdev info, group membership, vb2 queue and scratch DMA buffer, `qlock`-protected hardware buffers/list/sequence/running flag, route state, media bus code, active format, crop/compose, scaler callback, and alpha. `struct rvin_group` stores shared media device, notifier, platform info, VIN pointer array, link setup callback, and remote subdev slots. All state is runtime memory only.

## Dependencies And Integration Points
The header imports V4L2 async, controls, device, fwnode, and vb2 types plus kernel `kref`. It is the internal integration point between the VIN core/media graph, DMA engine, and V4L2 node implementation.

## Risks
The header centralizes locking expectations but does not enforce them; callers must honor `lock` for queue operations and `qlock` for hardware buffer state. Struct layout changes affect all three objects. `RVIN_REMOTES_MAX` depends on enum ordering and casts. Documentation typos in comments do not affect code but can mislead maintainers.

## Test Signals
Compile all VIN objects after structure/prototype changes, run sparse/lockdep for locking assumptions, verify `RCAR_VIN_NUM` indexed arrays are bounded by ID validation, and validate that all cross-file prototypes match definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar-vin/rcar-vin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar_drif.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar_drif.c

## Purpose
`rcar_drif.c` implements the R-Car Gen3 Digital Radio Interface as a V4L2 SDR capture driver. DRIF is receive-only, clocked by an external tuner/master, and uses SYS-DMAC to move FIFO samples to memory. One or two internal channels can be bonded; the driver exposes a single SDR video node after an async tuner subdevice binds.

## Important APIs, Types, And Functions
Core state types are `struct rcar_drif` for one internal hardware channel, `struct rcar_drif_sdr` for the grouped SDR device, `struct rcar_drif_hwbuf` for coherent DMA chunks, `struct rcar_drif_frame_buf` for userspace vb2 buffers, and `struct rcar_drif_format` for SDR formats. Main functions cover DMA channel allocation, coherent buffer allocation, MDR format programming, cyclic DMA queueing, RX start/stop, vb2 callbacks, SDR ioctls, tuner ioctl forwarding, async notifier callbacks, DT endpoint/bonding parsing, probe/remove, and stub PM callbacks.

## Control Flow
Probe creates one channel, gets clock and MMIO, records the FIFO physical base, and checks optional `renesas,bonding`. A non-primary bonded device only records channel 1 and waits for the primary. The primary allocates `rcar_drif_sdr`, links one or two channels, chooses a default format matching available channels, initializes vb2 with vmalloc-backed userspace buffers, registers `v4l2_device`, parses a tuner endpoint, and registers an async notifier. On notifier completion it imports tuner controls, registers subdev nodes, and registers the SDR video node.

On stream start, clocks are enabled, MDR defaults and selected format are written, DMA slave channels are requested/configured, coherent cyclic DMA buffers are allocated, each active channel is reset and submitted as cyclic DMA, status bits and DMA request interrupts are enabled, RX is enabled and polled, and `produced` resets. DMA callbacks serialize on `dma_lock`, mark channel buffer completion/overflow, wait for both bonded channel buffers when needed, copy hardware data into the next queued vb2 buffer, timestamp/sequence it, set payload, and complete it done or error. Stop disables RX, terminates DMA, returns queued vb2 buffers as error, frees coherent buffers, releases DMA channels, and disables clocks.

## State And Persistence
Runtime state includes channel mask from DT, current channel mask from selected format, current format pointer, MDR1 sync polarity/mode from endpoint properties, coherent hardware buffers, DMA handles, queued vb2 buffers, `produced` sequence, tuner subdev pointer, and controls copied from the tuner. No persistent storage exists. Suspend/resume are currently no-ops.

## Dependencies And Integration Points
The driver depends on platform devices, OF graph/phandle parsing, clocks, DMAengine cyclic transfers, coherent DMA memory, V4L2 async/control/device/event/ioctl frameworks, and vmalloc vb2 memory. It integrates with an external tuner subdevice for frequency/tuner ioctls and control handling, and with DT properties `sync-active`, `renesas,bonding`, and `renesas,primary-bond`.

## Risks
PM suspend/resume is explicitly unimplemented, so active streaming across system sleep is risky. Hardware DMA buffers are copied into vmalloc vb2 buffers, adding CPU cost and possible latency under high sample rates. If userspace queues too slowly, samples are dropped and sequence gaps appear. Bonded two-channel capture depends on synchronized DMA callbacks and status flags; races are mitigated by `dma_lock` but need stress testing. DMA buffer allocation error cleanup may leave earlier channel allocations to cleanup paths only. Tuner subdevice absence means no SDR node is registered.

## Test Signals
Validate single and bonded DT configurations, primary/non-primary probe ordering and defer behavior, tuner async bind/unbind, SDR node creation, all three PCU formats, one-channel selection when format needs fewer channels than hardware, cyclic DMA start/stop, overflow error completion, slow-consumer sequence gaps, clock/DMA cleanup on failures, streamoff buffer states, and suspend/resume expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rcar_drif.c -->
