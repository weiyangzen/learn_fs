# subset-b-004170 research

Grouped research report for the requested Allwinner sunxi media platform and Synopsys platform Kconfig/Makefile files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/Kconfig

Purpose: provides the menu entry and source aggregation point for Allwinner sunxi media platform drivers under the kernel media platform Kconfig tree.

Important APIs and symbols: no runtime APIs are declared. It emits a `comment "Sunxi media platform drivers"` and sources six child Kconfig files: `sun4i-csi`, `sun6i-csi`, `sun6i-mipi-csi2`, `sun8i-a83t-mipi-csi2`, `sun8i-di`, and `sun8i-rotate`.

Control flow: Kconfig evaluation enters this file from the parent media platform Kconfig and then evaluates each child driver option in order. The file itself has no conditions around child inclusion, so each child controls its own visibility and dependencies.

State and persistence: selected symbols persist only in the kernel build configuration. There is no runtime state.

Dependencies and integration points: integrates the sunxi capture, MIPI CSI-2, deinterlace, and rotation drivers into the V4L2 media platform menu. The corresponding directory Makefile builds the same child directories unconditionally through `obj-y` so child Makefiles can gate objects by config symbols.

Risks: adding a new sunxi media driver requires updating this source list or the option will be invisible in configuration. Ordering can affect menu readability but not runtime behavior.

Test signals: `menuconfig` should show all six child options when dependencies are satisfiable. `allmodconfig` and `COMPILE_TEST` builds validate that every sourced child Kconfig parses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/Makefile

Purpose: delegates sunxi media platform builds to the six child driver directories.

Important APIs and entries: `obj-y` includes `sun4i-csi/`, `sun6i-csi/`, `sun6i-mipi-csi2/`, `sun8i-a83t-mipi-csi2/`, `sun8i-di/`, and `sun8i-rotate/`.

Control flow: kbuild descends into each child directory during media platform builds. The actual object selection is controlled by each child Makefile through its Kconfig symbol.

State and persistence: no runtime state. Build output is determined by child `obj-$(CONFIG_...)` entries.

Dependencies and integration points: mirrors the top-level sunxi Kconfig sourcing and keeps all child drivers reachable from the platform media build.

Risks: if a child directory is removed or renamed without updating this Makefile, kbuild traversal fails. If a child Kconfig is added without a matching Makefile descent, the option can be selected without producing objects.

Test signals: kernel build coverage for `drivers/media/platform/sunxi/` with each child driver enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/Kconfig

Purpose: defines the build option for the Allwinner A10 camera sensor interface V4L2 driver.

Important APIs and symbols: `VIDEO_SUN4I_CSI` is a tristate option. It depends on `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, `COMMON_CLK`, `RESET_CONTROLLER`, `HAS_DMA`, and `ARCH_SUNXI || COMPILE_TEST`. It selects `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `VIDEOBUF2_DMA_CONTIG`, and `V4L2_FWNODE`.

Control flow: when selected, the directory Makefile links the `sun4i-csi.o` module from core, DMA, and V4L2 implementation files. The help text identifies the module name as `sun4i_csi`.

State and persistence: only affects persistent kernel build configuration. Runtime state is in the driver C files.

Dependencies and integration points: declares the media controller, V4L2 subdevice, fwnode graph, and DMA-contiguous buffer dependencies needed by the sun4i CSI media pipeline.

Risks: missing `HAS_DMA` or clock/reset dependencies would make runtime resource acquisition impossible. The option is narrow to A10-class CSI but also covers compatibles listed in the implementation.

Test signals: Kconfig visibility under sunxi or `COMPILE_TEST`, module build as `sun4i-csi.o`, and successful dependency auto-selection in `allyesconfig`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/Makefile

Purpose: links the sun4i CSI driver from its core, DMA, and V4L2 source files.

Important APIs and entries: `sun4i-csi-y` contains `sun4i_csi.o`, `sun4i_dma.o`, and `sun4i_v4l2.o`; `obj-$(CONFIG_VIDEO_SUN4I_CSI)` emits the composite `sun4i-csi.o`.

Control flow: kbuild compiles each component and links them into one module or built-in object according to `VIDEO_SUN4I_CSI`.

State and persistence: no runtime state. It preserves the module boundary between the platform driver, buffer/IRQ engine, and V4L2 ioctl/subdev layer.

Dependencies and integration points: consumes the Kconfig symbol in the same directory and exports no separate modules for the subcomponents.

Risks: adding a source file without this list would silently omit functionality from the module. Renaming any object requires synchronized updates here.

Test signals: `make M=drivers/media/platform/sunxi/sun4i-csi` with `CONFIG_VIDEO_SUN4I_CSI=m` should produce one module containing all three objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_csi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_csi.c

Purpose: implements the platform-driver, resource, media-device, async-notifier, and runtime-PM backbone for the sun4i/sun7i CSI capture driver.

Important APIs and functions: module entry is `module_platform_driver(sun4i_csi_driver)`. Main lifecycle functions are `sun4i_csi_probe`, `sun4i_csi_remove`, `sun4i_csi_runtime_resume`, and `sun4i_csi_runtime_suspend`. Async media callbacks are `sun4i_csi_notify_bound` and `sun4i_csi_notify_complete`. Local trait data is held in `struct sun4i_csi_traits` and selected by `sun4i_csi_of_match`.

Control flow: probe allocates `struct sun4i_csi`, maps registers, gets IRQ, clocks, and reset, initializes a media device and local CSI subdevice, initializes media pads for the subdevice and video node, registers the DMA/V4L2 base through `sun4i_csi_dma_register`, parses the fwnode endpoint, registers a V4L2 async notifier, then enables runtime PM. When a remote sensor subdevice binds, the driver finds the source pad and stores the parallel bus configuration. Notifier completion registers the local subdevice, registers the video device, registers the media device, creates immutable source-to-CSI and CSI-to-video links, and registers subdevice devnodes. Runtime resume deasserts reset, enables bus/RAM/optional ISP clocks, and writes `CSI_EN_REG`; suspend disables clocks and asserts reset.

State and persistence: persistent driver state is in `struct sun4i_csi`, including MMIO base, clocks, reset, traits, media/V4L2/video/subdev objects, bus configuration, notifier, and buffer queue state initialized by the DMA file. Hardware register state is volatile and rebuilt on stream start or runtime resume.

Dependencies and integration points: depends on platform resources, device tree compatibles `allwinner,sun4i-a10-csi1` and `allwinner,sun7i-a20-csi0`, V4L2 async/fwnode APIs, media-controller links, videobuf2 DMA-contig, common clock, reset, and runtime PM. It delegates capture queue setup to `sun4i_csi_dma_register` and video node setup to `sun4i_csi_v4l2_register`.

Risks: `clk_set_rate` and `clk_prepare_enable` are called on `isp_clk` even for traits without ISP; nullable clock handling depends on the clock API tolerating NULL pointers. Error paths after notifier completion can leave already registered entities if later steps fail. Link validation for the video entity only warns once and always succeeds.

Test signals: platform probe/remove on A10/A20 device-tree nodes, media graph link creation with a remote sensor, runtime suspend/resume, module unload, and streaming smoke tests covering both `has_isp` false and true traits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_csi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_csi.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_csi.h

Purpose: central header for sun4i CSI register definitions, format descriptions, shared device state, and cross-file function declarations.

Important APIs and types: defines register offsets and bit-field helpers for enable, configuration, capture control, buffer addresses, interrupts, window size, and buffer length. It defines CSI input/output/YUV sequence enums, media pad enum `csi_subdev_pads`, `struct sun4i_csi_format`, and `struct sun4i_csi`. Exported internal APIs are `sun4i_csi_find_format`, `sun4i_csi_dma_register`, `sun4i_csi_dma_unregister`, and `sun4i_csi_v4l2_register`; subdev ops are exposed as externs.

Control flow: C files include this header to share the common device object. Core probe populates resources and media entities, DMA code consumes register constants and queue fields, and V4L2 code consumes format tables and subdev declarations.

State and persistence: `struct sun4i_csi` owns all runtime state: device resources, current double-buffer slots, scratch DMA buffer, bus config, V4L2/media/video objects, local subdev, async remote-source info, mutex/spinlock, vb2 queue, pending buffer list, and sequence counter.

Dependencies and integration points: pulls in media-device, V4L2 async/dev/fwnode, and videobuf2 core headers. It is the private ABI between `sun4i_csi.c`, `sun4i_dma.c`, and `sun4i_v4l2.c`.

Risks: register bit macros do no range checking. `CSI_MAX_WIDTH` and `CSI_MAX_HEIGHT` are broad constants, while actual traits contain lower `max_width` data that is not enforced by this header or current format paths. State fields are shared between IRQ and user paths and require correct lock discipline.

Test signals: compile coverage catches cross-file declaration drift; runtime buffer cycling validates `current_buf`, scratch, and register offset assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_csi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_dma.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_dma.c

Purpose: implements videobuf2 capture queue handling, DMA buffer programming, stream start/stop, and frame-done interrupt processing for sun4i CSI.

Important APIs and functions: public internal functions are `sun4i_csi_dma_register` and `sun4i_csi_dma_unregister`. Main vb2 callbacks are `sun4i_csi_queue_setup`, `sun4i_csi_buffer_prepare`, `sun4i_csi_buffer_queue`, `sun4i_csi_start_streaming`, and `sun4i_csi_stop_streaming`. IRQ entry is `sun4i_csi_irq`. Buffer helpers include scratch setup, slot fill, slot flip, and `return_all_buffers`.

Control flow: queue registration initializes locks, buffer list, vb2 queue, V4L2 device, and IRQ. Queued buffers are appended under `qlock`. Start streaming finds the configured CSI format, allocates a coherent scratch buffer large enough for all planes, starts the media pipeline, programs active width/height, polarities, input/output format, line length, two hardware buffer slots, double buffering, and frame-done interrupt, starts capture, then starts the source subdevice stream. On each frame interrupt, the status is acknowledged, the sequence number is assigned, the completed slot is returned to vb2, and the next queued or scratch buffer is programmed. Stop streaming stops the source and hardware, returns active/queued buffers as error, stops the pipeline, and frees the scratch buffer.

State and persistence: state is volatile in `csi->buf_list`, `current_buf[2]`, `scratch`, and `sequence`. DMA addresses are written directly to hardware registers and are valid only while buffers are queued and the device is powered. The scratch buffer prevents last-frame underruns when user buffers run out.

Dependencies and integration points: depends on videobuf2 V4L2 and DMA-contig helpers, media pipeline start/stop, V4L2 subdev `s_stream`, and register definitions from `sun4i_csi.h`. It relies on the V4L2 layer to populate `csi->fmt` and the core layer to register resources.

Risks: `q->min_queued_buffers = 3` with only two hardware slots relies on the scratch-buffer strategy and userspace queue depth. Error paths after `sun4i_csi_capture_start` must unwind hardware and pipeline consistently. No explicit overflow/line error interrupts are handled, only frame done. Format configuration writes active width as `width * 2`, which is format-specific and may not generalize if new formats are added.

Test signals: vb2 mmap and dmabuf streaming, queue underrun with scratch-buffer use, source subdev stream failure paths, IRQ-driven sequence increments, stop-streaming buffer states, and stress tests with rapid streamon/streamoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_v4l2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_v4l2.c

Purpose: implements V4L2 ioctl, file-operation, format, and local subdevice pad handling for the sun4i CSI video node.

Important APIs and functions: exported internals are `sun4i_csi_find_format`, `sun4i_csi_subdev_ops`, `sun4i_csi_subdev_internal_ops`, and `sun4i_csi_v4l2_register`. It defines the format table, ioctl ops for querycap, enum/get/set/try mplane capture formats, input selection, and vb2 ioctls, plus file open/release and subdev pad operations.

Control flow: `sun4i_csi_v4l2_register` sets a default YUV420M capture format and default YUYV mbus subdev format, attaches file/ioctl ops, and registers the video device. Format try/set clamps and aligns dimensions to the single supported format's subsampling, fills per-plane bytesperline and sizeimage, and stores the chosen format. File open resumes runtime PM, powers the media pipeline, then opens a V4L2 file handle; release tears down vb2 state through `_vb2_fop_release`, drops pipeline PM, and runtime-suspends. Subdev init sets default sink format; get/set operate on try or active state and currently allow sink size/code updates.

State and persistence: active capture format is stored in `csi->fmt`; active subdev format is stored in `csi->subdev_fmt`. Try-state formats live in V4L2 subdev state. PM usage counts persist while file handles are open.

Dependencies and integration points: integrates with V4L2 ioctl core, videobuf2 V4L2 fops, V4L2 media controller PM, runtime PM, and the shared queue from `sun4i_dma.c`.

Risks: only one media-bus/pixel-format combination is supported. `s_fmt` does not check `vb2_is_busy`, so active queue use could be sensitive to V4L2 core serialization assumptions. Subdev source-pad format mirrors the stored format without explicit source propagation or validation. Capture width/height maxima do not use per-compatible `traits`.

Test signals: `v4l2-ctl --all`, format enumeration/try/set, open/close runtime PM balancing, mplane buffer requests, media-ctl format negotiation, and negative tests for unsupported inputs and formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_v4l2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/Kconfig

Purpose: defines the build option for the Allwinner A31-family CSI bridge/capture driver.

Important APIs and symbols: `VIDEO_SUN6I_CSI` is a tristate depending on platform media, video, sunxi or compile-test, PM, common clock, reset, and DMA support. It selects media controller, V4L2 subdevice API, videobuf2 DMA-contig, V4L2 fwnode, and regmap MMIO.

Control flow: selecting this symbol causes the Makefile to link `sun6i-csi.o` from core, bridge, and capture objects.

State and persistence: build configuration only. Runtime state is owned by `struct sun6i_csi_device`.

Dependencies and integration points: enables an A31 CSI block found on A83T, H3, V3/V3s, and A64, with optional ISP integration handled at runtime.

Risks: the driver requires PM, clocks, reset, DMA, and regmap; platform data or device tree omissions surface at probe time.

Test signals: Kconfig dependency resolution, module build, and compile-test builds with `REGMAP_MMIO` selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/Makefile

Purpose: links the sun6i CSI driver from platform, bridge, and capture components.

Important APIs and entries: `sun6i-csi-y` includes `sun6i_csi.o`, `sun6i_csi_bridge.o`, and `sun6i_csi_capture.o`; `obj-$(CONFIG_VIDEO_SUN6I_CSI)` builds `sun6i-csi.o`.

Control flow: kbuild creates a single composite module or built-in object when `VIDEO_SUN6I_CSI` is enabled.

State and persistence: no runtime state.

Dependencies and integration points: maps the Kconfig symbol to the implementation split used by the driver headers.

Risks: source/object list drift can omit a major subsystem because bridge and capture are not separately selectable.

Test signals: module builds with all three objects linked and no undefined references between the components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi.c

Purpose: implements the platform-driver, resource management, runtime PM, interrupt dispatch, and optional ISP/V4L2 media-device ownership for the sun6i CSI block.

Important APIs and functions: exported integration hook is `sun6i_csi_isp_complete`. Main local functions include `sun6i_csi_probe`, `sun6i_csi_remove`, `sun6i_csi_resources_setup`, `sun6i_csi_v4l2_setup`, `sun6i_csi_interrupt`, `sun6i_csi_resume`, and `sun6i_csi_suspend`. Variant data sets module clock rate per compatible.

Control flow: probe allocates `struct sun6i_csi_device`, maps registers through regmap, acquires module/RAM clocks and shared reset, sets an exclusive module-clock rate, requests a shared IRQ, enables runtime PM, detects an optional ISP graph endpoint, registers its own media/V4L2 devices if no ISP is present, sets up the bridge subdevice, and sets up capture immediately or later through ISP completion. The IRQ reads channel status and enables, ignores unrelated or disabled status, resets CSI on FIFO/HB overflow, dispatches frame-done to sequence update, dispatches VS to buffer sync, then clears status.

State and persistence: `struct sun6i_csi_device` stores device resources, regmap, clocks, reset, V4L2/media ownership, bridge state, capture state, and `isp_available`. Hardware state is volatile and rebuilt when the bridge starts streaming. The exclusive clock-rate reservation persists between resources setup and cleanup.

Dependencies and integration points: depends on regmap MMIO with bus clock, runtime PM, media/V4L2 core, V4L2 async bridge/capture setup, and device tree compatibles for A31, A83T, H3, V3s, and A64. Optional ISP integration reuses the remote subdevice's V4L2/media devices and registers capture after async binding.

Risks: IRQ overflow recovery toggles the CSI enable bit and can drop frames. Shared IRQ handling must return `IRQ_NONE` only for truly unrelated status. ISP detection is graph-based and warns if the kernel lacks `CONFIG_VIDEO_SUN6I_ISP`, but then proceeds without ISP support. Cleanup calls capture cleanup even when capture setup never completed, relying on setup guards.

Test signals: probe/remove for each compatible clock rate, runtime PM resume/suspend, shared IRQ behavior, FIFO overflow recovery, no-ISP standalone media graph, ISP-connected graph completion, and streaming with frame/VS interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi.h

Purpose: top-level private header for the sun6i CSI driver, tying together platform resources, V4L2/media state, bridge state, and capture state.

Important APIs and types: defines `SUN6I_CSI_NAME`, `SUN6I_CSI_DESCRIPTION`, port enum values for parallel, MIPI CSI-2, and ISP graph ports, `struct sun6i_csi_buffer`, `struct sun6i_csi_v4l2`, `struct sun6i_csi_device`, and `struct sun6i_csi_variant`. Declares `sun6i_csi_isp_complete`.

Control flow: included by platform, bridge, and capture implementation files. The platform file owns allocation and resource setup; bridge and capture files operate on the embedded substructures.

State and persistence: `struct sun6i_csi_device` is the persistent per-device driver object. It holds both standalone V4L2/media objects and pointers to the active V4L2/media ownership, allowing ISP-backed and standalone modes to share capture setup.

Dependencies and integration points: includes V4L2 device and vb2 V4L2 headers plus the bridge/capture private headers. It is the internal ABI between the three sun6i CSI objects.

Risks: because bridge and capture are embedded in one object, initialization order matters. The `isp_available` mode changes who owns V4L2/media devices and makes async completion paths more sensitive to duplicate bound callbacks.

Test signals: compile coverage for cross-file type use, ISP and no-ISP probe paths, and static analysis for initialization before use of `v4l2_dev` and `media_dev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_bridge.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_bridge.c

Purpose: implements the sun6i CSI media bridge subdevice, input format tables, hardware interface configuration, async source discovery, and streaming control between external sensors/MIPI receivers and the capture video node.

Important APIs and functions: exported internals are `sun6i_csi_bridge_dimensions`, `sun6i_csi_bridge_format`, `sun6i_csi_bridge_format_find`, `sun6i_csi_bridge_setup`, and `sun6i_csi_bridge_cleanup`. Important local paths include IRQ enable/disable/clear, bridge enable/disable, parallel/MIPI configuration, format register programming, `sun6i_csi_bridge_s_stream`, pad get/set/enum operations, async bound/complete callbacks, and source setup.

Control flow: setup initializes a V4L2 subdevice with sink/source pads, registers it either as an async subdevice for ISP mode or as a child of the local V4L2 device, initializes an async notifier, and adds expected parallel and MIPI CSI-2 remote endpoints from graph ports. Binding stores the remote subdevice, optionally completes ISP capture setup, and creates a media link; parallel is preferred/enabled when present, otherwise MIPI is enabled. `s_stream(1)` finds the unique active remote source, resumes runtime PM, clears interrupts, configures the input bus, writes channel format based on active mbus/capture formats, configures capture if needed, stages a pending buffer, enables interrupts and CSI capture, then starts the upstream subdevice. `s_stream(0)` stops upstream, disables interrupts and CSI, and drops PM.

State and persistence: active mbus format is stored in `bridge.mbus_format` under a mutex. Source structures retain parsed endpoint details, expected flags, and bound subdev pointers. Hardware register state is written on each stream start and is not persistent across runtime suspend.

Dependencies and integration points: depends on V4L2 fwnode endpoint parsing, async notifier APIs, media links, regmap, runtime PM, register macros, capture format helpers, and optional ISP V4L2 ownership. It is the control point where capture format choices influence CSI channel output format.

Risks: the format table contains duplicate UYVY entries, which is harmless for first-match lookup but confusing. Only one active remote source is allowed by `media_pad_remote_pad_unique`. Error paths in stream start go through the common disable block, which also powers off PM after partial upstream or hardware failures. Unsupported bus types/widths only warn in configuration, which may leave incomplete register setup. Single-channel assumptions limit multi-VC CSI use.

Test signals: media graph creation with parallel and MIPI sources, source-priority behavior, subdev format get/set, link validation, streamon/streamoff with upstream sensor, interrupt enable/clear programming, and negative tests for unsupported endpoint bus types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_bridge.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_bridge.h

Purpose: declares the bridge subdevice data model and helper APIs for sun6i CSI.

Important APIs and types: defines bridge pad indexes, `struct sun6i_csi_bridge_format`, source tracking structs, async-subdev wrapper, and `struct sun6i_csi_bridge`. Declares helpers for dimensions, format, format lookup, setup, and cleanup.

Control flow: the platform code calls setup/cleanup. Capture code queries bridge dimensions and mbus format for link validation and hardware configuration. Bridge implementation uses the source structures for async endpoint binding.

State and persistence: stores active media-bus format, lock, subdevice, notifier, pads, parallel source, and MIPI source. Source endpoint data persists after fwnode parsing and is used during stream-time bus configuration.

Dependencies and integration points: includes V4L2 device and fwnode types and forward-declares `struct sun6i_csi_device`. It mediates between the capture object and external sensor/MIPI subdevices.

Risks: the `pads` array is declared as `[2]` rather than by the enum count macro, so future pad-count changes require careful updates. Source selection depends on stored subdev pointers matching the active remote entity.

Test signals: build coverage and runtime async binding validate the header contracts; media graph introspection should show two bridge pads and correct links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_bridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_capture.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_capture.c

Purpose: implements the sun6i CSI capture video node, supported pixel-format table, VB2 queue handling, hardware output-size/buffer programming, capture state machine, and media-link validation.

Important APIs and functions: exported internals are `sun6i_csi_capture_dimensions`, `sun6i_csi_capture_format`, `sun6i_csi_capture_format_find`, `sun6i_csi_capture_configure`, `sun6i_csi_capture_state_update`, `sun6i_csi_capture_sync`, `sun6i_csi_capture_frame_done`, `sun6i_csi_capture_setup`, and `sun6i_csi_capture_cleanup`. Major local paths include buffer address programming, state cleanup/complete, queue setup/prepare/queue/start/stop, format prepare and ioctls, file open/close, and `sun6i_csi_capture_link_validate`.

Control flow: setup initializes state locks and queue, creates a sink pad for the video device, sets a default 1280x720 Bayer format, registers the video node, and creates a bridge-to-video link. Userspace sets a single-planar capture format; stream start starts the media pipeline, marks capture streaming, and calls bridge `s_stream(1)`. Bridge stream start then configures the capture hardware and calls `sun6i_csi_capture_state_update` to program a pending buffer. VS interrupts call `sync`, which completes the current buffer, promotes pending to current, and stages another pending buffer. Frame-done interrupts increment the sequence counter.

State and persistence: `sun6i_csi_capture_state` tracks queued buffers plus `pending`, `current`, `complete`, sequence, streaming, and setup flags under a spinlock. `capture.format` stores the active V4L2 format under the queue mutex. Hardware FIFO addresses and size registers are programmed from the active queued buffer.

Dependencies and integration points: depends on V4L2 mem2mem-like VB2 helpers for capture, DMA-contig, media-controller link validation, V4L2 format info, bridge helpers, and regmap register definitions. It relies on the bridge for stream sequencing and interrupt enablement.

Risks: the driver exposes one vb2 plane even for multi-component formats and manually computes component offsets inside the same DMA buffer. Queue cleanup iterates list entries and then reinitializes the list; correctness depends on no concurrent enqueue after stream stop locking. Sequence is incremented on frame done but buffers complete on VS, so unusual interrupt ordering can affect sequence assignment. Some unsupported pixel formats lack `v4l2_format_info` and are handled as special cases.

Test signals: format enumeration and sizeimage for all listed pixel formats, link validation for RAW/RGB/YUV mbus combinations, streaming with two or more buffers, underrun/no-pending behavior, frame sequence monotonicity, dmabuf import, and ISP vs non-ISP link flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_capture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_capture.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_capture.h

Purpose: declares the capture video-node data model, supported-format metadata shape, capture state machine, and internal capture APIs for sun6i CSI.

Important APIs and types: defines capture name and min/max dimensions, `struct sun6i_csi_capture_format`, `struct sun6i_csi_capture_format_match`, `struct sun6i_csi_capture_state`, and `struct sun6i_csi_capture`. Declares helpers for active dimensions/format, format lookup, hardware configure, state update/sync/frame_done, setup, and cleanup.

Control flow: platform/ISP paths call capture setup/cleanup; bridge calls capture configure and state update during stream start; IRQ dispatch calls frame_done and sync.

State and persistence: queue, locks, pending/current/complete buffers, sequence, streaming, and setup state persist for the device lifetime after setup. Active user format persists in `capture.format` until changed while queues are idle.

Dependencies and integration points: includes V4L2 device types and forward-declares `struct sun6i_csi_device`. It is the private contract between platform, bridge, IRQ, and capture implementation files.

Risks: `#undef current` avoids a macro collision for the field named `current`, which is a portability hint for kernel macro namespace issues. Future state-machine changes must preserve spinlock protection around the three buffer slots.

Test signals: compile coverage, IRQ-driven state transitions, and stream stop cleanup for each buffer slot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_capture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_reg.h

Purpose: defines MMIO register offsets and bit-field helpers for the sun6i CSI controller and capture channel.

Important APIs and constants: covers global enable, interface configuration, capture control, pattern generator, channel config, input/output format constants, FIFO addresses, channel status, interrupt enable/status, frame/line size, buffer length, flip size, counters, and address conversion through `SUN6I_CSI_ADDR_VALUE`.

Control flow: no executable control flow. Bridge code writes interface and channel format registers; capture code writes FIFO addresses, sizes, and buffer lengths; IRQ code reads and clears interrupt status.

State and persistence: no software state. The macros describe volatile hardware state programmed during runtime PM and stream start.

Dependencies and integration points: includes `linux/kernel.h` for `BIT` and `GENMASK`. It is consumed by all sun6i CSI implementation files and must match hardware manuals/BSP behavior.

Risks: comments note that Allwinner documentation inverts some positive/negative and frame/field definitions; misuse can cause polarity or interlacing bugs. Bit-field macros assume caller-supplied values fit expected ranges and silently mask overflow. Address conversion shifts DMA addresses by two, matching hardware word-addressing assumptions.

Test signals: hardware capture with parallel and MIPI sources, polarity tests, interlaced input tests, FIFO overflow interrupt tests, and register dumps compared with known-good BSP programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/sun6i_csi_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/Kconfig

Purpose: defines the build option for the Allwinner A31/V3 MIPI CSI-2 receiver bridge driver.

Important APIs and symbols: `VIDEO_SUN6I_MIPI_CSI2` is a tristate depending on V4L platform/video support, sunxi or compile-test, PM, common clock, reset, and `PHY_SUN6I_MIPI_DPHY`. It selects media controller, V4L2 subdevice API, V4L2 fwnode, generic MIPI D-PHY helpers, and regmap MMIO.

Control flow: enabling the option builds the single-object `sun6i-mipi-csi2` driver.

State and persistence: build configuration only.

Dependencies and integration points: ties the CSI-2 bridge to an external sun6i MIPI D-PHY provider and the media-controller graph.

Risks: the hard dependency on `PHY_SUN6I_MIPI_DPHY` means the receiver is not available unless the external PHY driver is enabled. It supports only the formats implemented in the C file.

Test signals: Kconfig selection should pull generic D-PHY helpers and regmap; module build should work under `COMPILE_TEST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/Makefile

Purpose: maps `VIDEO_SUN6I_MIPI_CSI2` to the A31 MIPI CSI-2 receiver object.

Important APIs and entries: `sun6i-mipi-csi2-y` contains `sun6i_mipi_csi2.o`; `obj-$(CONFIG_VIDEO_SUN6I_MIPI_CSI2)` builds the module.

Control flow: kbuild emits one module or built-in object from one source file.

State and persistence: no runtime state.

Dependencies and integration points: consumed by the sunxi parent Makefile and the child Kconfig symbol.

Risks: minimal; future file splits require updating `sun6i-mipi-csi2-y`.

Test signals: targeted module build with the config enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2.c

Purpose: implements the Allwinner A31 MIPI CSI-2 receiver as a V4L2 async subdevice bridge with runtime PM, regmap configuration, D-PHY control, sensor binding, and media links.

Important APIs and functions: module entry is `module_platform_driver(sun6i_mipi_csi2_platform_driver)`. Key paths include format lookup, controller enable/disable/configure, `sun6i_mipi_csi2_s_stream`, subdev pad enum/get/set/init, async notifier bound/source setup, bridge setup/cleanup, resources setup/cleanup, runtime suspend/resume, and probe/remove.

Control flow: probe maps registers through `devm_regmap_init_mmio_clk`, gets the module clock, reserves a 297 MHz clock rate, gets shared reset and external D-PHY, initializes the PHY, enables runtime PM, then registers the bridge subdevice and optional sensor notifier. When a remote sensor binds, the driver creates an immutable link from sensor source pad to CSI-2 sink and stores `source_subdev`. On stream start, it resumes PM, reads the upstream sensor `V4L2_CID_PIXEL_RATE`, computes MIPI D-PHY timing from pixel rate, bits-per-pixel, and lane count, resets/configures the PHY, writes controller reset/version/unpack/config/VC-DT registers, enables the controller, powers the PHY, and starts the sensor. Stream stop stops the sensor, powers off the PHY, disables the controller, and drops PM.

State and persistence: `struct sun6i_mipi_csi2_device` stores regmap, clock, reset, external PHY, and bridge state. The active mbus format and parsed lane endpoint persist in the bridge. Hardware state is reconstructed per stream start and lost across runtime suspend.

Dependencies and integration points: depends on media CSI-2 data type constants, V4L2 control API for pixel rate, V4L2 async/fwnode, generic PHY MIPI D-PHY helpers, regmap, runtime PM, and an external `dphy` provider. Its source pad is intended to feed the sun6i CSI bridge MIPI input.

Risks: only RAW8/RAW10 Bayer formats are supported. Missing or zero `V4L2_CID_PIXEL_RATE` prevents streaming. Only virtual channel 0 is effectively configured for use. D-PHY clock-rate debug output accounts for DDR manually but does not alter the generic helper result. If no sensor endpoint exists, the subdevice still registers but has no source and returns `-ENODEV` on stream.

Test signals: media graph binding to a sensor and sun6i CSI, stream start with valid pixel-rate control, lane-count parsing, D-PHY configure/power sequencing, register dumps around version-enable toggling, and negative tests for missing source or pixel rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2.h

Purpose: declares the A31 MIPI CSI-2 receiver device, bridge, pad, and format data structures.

Important APIs and types: defines the driver name, sink/source pad enum, `struct sun6i_mipi_csi2_format`, `struct sun6i_mipi_csi2_bridge`, and `struct sun6i_mipi_csi2_device`.

Control flow: the implementation stores subdev, pads, endpoint, notifier, active mbus format, and source subdev in the bridge structure; platform resource setup fills the device structure.

State and persistence: active endpoint lane data and mbus format persist after setup and format negotiation; source subdev persists after async binding.

Dependencies and integration points: includes PHY, regmap, reset, V4L2 device, and V4L2 fwnode headers. It is private to the driver source.

Risks: no public functions are declared, so all behavior is confined to one C file. Future multi-source or multi-channel support would require expanding the bridge state model.

Test signals: compile coverage and runtime subdev registration validate structure use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2_reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2_reg.h

Purpose: defines register offsets and bit masks for the A31 MIPI CSI-2 receiver.

Important APIs and constants: covers controller control bits, configuration lane/channel fields, VC/data-type receive routing, packet number/version registers, per-channel interrupt enable/pending bits, current packet header/ECC/checksum/frame/line registers, and channel register stride macro.

Control flow: no executable code. The C file writes control/config/VC-DT and clears interrupt-pending registers; interrupt masks are defined for future or diagnostic use.

State and persistence: hardware register descriptions only.

Dependencies and integration points: relies on `BIT` and `GENMASK` being available through included kernel headers before use. It is consumed by the A31 CSI-2 implementation.

Risks: `SUN6I_MIPI_CSI2_CH_INT_PD_CLEAR` is `0xff`, clearing only low interrupt bits despite higher status bits being defined; this matches current usage but may be incomplete if more interrupt handling is added. Bit-field macros mask inputs rather than validating ranges.

Test signals: hardware stream start and register dump comparison with expected lane count/data type; future interrupt tests if channel interrupts are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/Kconfig

Purpose: defines the build option for the Allwinner A83T MIPI CSI-2 receiver plus integrated D-PHY driver.

Important APIs and symbols: `VIDEO_SUN8I_A83T_MIPI_CSI2` is a tristate depending on V4L platform/video support, sunxi or compile-test, PM, common clock, and reset. It selects media controller, V4L2 subdevice API, V4L2 fwnode, regmap MMIO, generic PHY, and generic MIPI D-PHY helpers.

Control flow: selecting the symbol builds a composite module containing the CSI-2 receiver and D-PHY provider.

State and persistence: build configuration only.

Dependencies and integration points: unlike the A31 driver, it provides its own D-PHY through the generic PHY framework.

Risks: it has no external PHY dependency, but device-tree consumers must still wire the integrated PHY provider correctly. Format support is limited to RAW8/RAW10 Bayer.

Test signals: Kconfig dependency selection, module build, and PHY provider registration on A83T-compatible nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/Makefile

Purpose: links the A83T MIPI CSI-2 receiver and its integrated D-PHY helper into one module.

Important APIs and entries: `sun8i-a83t-mipi-csi2-y` contains `sun8i_a83t_mipi_csi2.o` and `sun8i_a83t_dphy.o`; `obj-$(CONFIG_VIDEO_SUN8I_A83T_MIPI_CSI2)` emits the composite object.

Control flow: kbuild includes both controller and PHY provider code whenever the option is enabled.

State and persistence: no runtime state.

Dependencies and integration points: keeps the integrated PHY provider in the same module as the controller that owns its registers.

Risks: separating the D-PHY without adjusting module ownership would break resource sharing through `struct sun8i_a83t_mipi_csi2_device`.

Test signals: module build with both objects linked and no unresolved `sun8i_a83t_dphy_register`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_dphy.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_dphy.c

Purpose: registers and implements the integrated A83T MIPI D-PHY as a generic PHY provider backed by the CSI-2 controller's regmap.

Important APIs and functions: exported internal function is `sun8i_a83t_dphy_register`. PHY ops are `sun8i_a83t_dphy_configure`, `sun8i_a83t_dphy_power_on`, and `sun8i_a83t_dphy_power_off`.

Control flow: registration creates a devm-managed PHY, stores the CSI-2 device as PHY drvdata, and registers a simple OF PHY provider. Configure validates MIPI D-PHY options. Power-on writes reset/shutdown bits in the D-PHY control register and analog resistor/sink settings. Power-off clears the D-PHY control register.

State and persistence: the PHY object is devm-managed and tied to the controller device. Hardware state is limited to D-PHY control and analog registers and is changed on PHY power transitions.

Dependencies and integration points: depends on generic PHY APIs, MIPI D-PHY validation helpers, and shared regmap/register definitions from the A83T CSI-2 driver. It is consumed by the controller stream path through `csi2_dev->dphy`.

Risks: configure only validates generic timing and does not program timing-specific registers; power-on uses fixed analog values. The power-off function clears control but leaves analog register state untouched. There is no explicit reset op.

Test signals: PHY provider lookup by device tree, `phy_configure` validation with sensor pixel-rate-derived timings, power-on/off register traces, and stream bring-up on A83T hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_dphy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_dphy.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_dphy.h

Purpose: declares A83T D-PHY register definitions and the D-PHY registration hook.

Important APIs and constants: defines D-PHY control/status/analog register offsets, reset/shutdown/debug/status bits, initial control value, and analog field helpers. Declares `sun8i_a83t_dphy_register`.

Control flow: included by both D-PHY implementation and CSI-2 controller implementation so controller initialization can write D-PHY magic init values and resource setup can register the PHY provider.

State and persistence: no software state. Constants describe hardware state in the shared CSI-2 register space.

Dependencies and integration points: includes the A83T CSI-2 device header for the device type. It is the interface between the controller and integrated PHY provider.

Risks: several status bits are defined but not read by the implementation; bring-up diagnostics may need them. Fixed magic/init values are hardware-specific and poorly self-documenting.

Test signals: compile coverage and register traces during runtime resume and PHY power-on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_dphy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2.c

Purpose: implements the Allwinner A83T MIPI CSI-2 receiver bridge and coordinates the integrated D-PHY, clocks, reset, runtime PM, sensor async binding, and stream-time controller programming.

Important APIs and functions: module entry is `module_platform_driver(sun8i_a83t_mipi_csi2_platform_driver)`. Key functions include format lookup, `sun8i_a83t_mipi_csi2_init`, enable/disable/configure, `sun8i_a83t_mipi_csi2_s_stream`, pad operations, async notifier bound/source setup, bridge setup/cleanup, suspend/resume, resources setup/cleanup, and probe/remove.

Control flow: probe maps registers with regmap, gets module/MIPI/misc clocks, reserves the module rate at 297 MHz, gets shared reset, registers the integrated D-PHY, enables runtime PM, and registers the bridge subdevice plus optional upstream sensor notifier. Runtime resume deasserts reset, enables all three clocks, and writes BSP-derived initialization values including reserved hardware-lock registers. Stream start resumes PM, obtains upstream pixel rate, computes D-PHY options from pixel rate/bpp/lane count, resets/configures the PHY, writes controller reset/config/VC-DT registers, enables sync, powers on the PHY, and starts the source subdevice. Stop reverses source, PHY, controller, and PM.

State and persistence: `struct sun8i_a83t_mipi_csi2_device` stores regmap, clocks, reset, integrated PHY, and bridge state. Active mbus format, parsed endpoint, and source subdev persist in the bridge. Controller magic initialization is repeated on runtime resume.

Dependencies and integration points: depends on V4L2 async/fwnode, media-controller subdevs, V4L2 pixel-rate control, generic PHY MIPI D-PHY helpers, regmap, common clocks, reset, and the local D-PHY provider. The source pad feeds downstream CSI/ISP media graph entities.

Risks: only RAW8/RAW10 Bayer formats are supported. Several magic register values come from BSP behavior and are required to avoid unsolicited interrupts, but their semantics are not fully known. Only virtual channel 0 is configured for real payload use. Stream start fails if the upstream sensor lacks pixel rate or lane count. Cleanup calls `phy_exit` although the PHY was created by the local provider, so lifetime assumptions should be checked against generic PHY semantics.

Test signals: A83T media graph binding, runtime resume register initialization, sensor stream with valid pixel rate, D-PHY power sequencing, RAW8/RAW10 capture, stream stop/restart, and negative tests for missing graph endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2.h

Purpose: declares the A83T MIPI CSI-2 receiver's device, bridge, pad, and format structures.

Important APIs and types: defines driver name, sink/source pad enum, `struct sun8i_a83t_mipi_csi2_format`, `struct sun8i_a83t_mipi_csi2_bridge`, and `struct sun8i_a83t_mipi_csi2_device`.

Control flow: the controller implementation fills the device resources and bridge state; the D-PHY implementation receives the device pointer for shared regmap access.

State and persistence: bridge state stores active mbus format, parsed CSI-2 endpoint, async notifier, and bound source subdev. Device state stores three clocks, reset, regmap, and integrated PHY.

Dependencies and integration points: includes generic PHY, regmap, reset, V4L2 device, and fwnode headers. It is the private shared header between controller and D-PHY files.

Risks: adding more pads, channels, or PHY timing state requires expanding fixed-size structures. The bridge assumes one upstream source.

Test signals: compile coverage and runtime graph registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2_reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2_reg.h

Purpose: defines A83T MIPI CSI-2 receiver register offsets, magic initialization values, interrupt status/mask bits, and configuration field helpers.

Important APIs and constants: covers version/control/RX packet/reserved registers, extensive interrupt status and mask bit definitions for SOT/ECC/CRC/frame/line/data errors, configuration bits for sync, unpack, lane/channel count, sync delay, and VC/data-type routing registers.

Control flow: no executable flow. The controller writes init values during resume, configures lane/channel/unpack/sync settings during stream start, and writes VC-DT routing for channel 0.

State and persistence: hardware register description only.

Dependencies and integration points: consumed by `sun8i_a83t_mipi_csi2.c`; D-PHY register definitions live in the sibling D-PHY header.

Risks: many interrupt bits are defined but no IRQ handler is implemented in this driver, so error visibility depends on downstream failure signals or debug reads. Magic values for reserved registers are hardware-specific. Field helpers mask values without runtime validation.

Test signals: register-dump validation after runtime resume and stream start; hardware error-injection or noisy-link tests if interrupt handling is later added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/Kconfig

Purpose: defines the build option for the Allwinner deinterlace V4L2 mem2mem driver.

Important APIs and symbols: `VIDEO_SUN8I_DEINTERLACE` is a tristate depending on V4L mem2mem drivers, video, sunxi or compile-test, common clock, reset, OF, and PM. It selects videobuf2 DMA-contig and `V4L2_MEM2MEM_DEV`.

Control flow: when enabled, the Makefile builds `sun8i-di.o`.

State and persistence: build configuration only.

Dependencies and integration points: exposes a deinterlace/scaling unit as a V4L2 memory-to-memory video device.

Risks: no media-controller dependency because it is an isolated mem2mem engine. Runtime requires clocks, reset, IRQ, and coherent DMA.

Test signals: module build and V4L2 mem2mem device registration on compatible hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/Makefile

Purpose: maps the deinterlace Kconfig symbol to its single implementation object.

Important APIs and entries: `obj-$(CONFIG_VIDEO_SUN8I_DEINTERLACE) += sun8i-di.o`.

Control flow: kbuild compiles and links `sun8i-di.c` when the option is enabled.

State and persistence: no runtime state.

Dependencies and integration points: consumed by the sunxi parent Makefile.

Risks: minimal unless the driver is split into multiple source files.

Test signals: targeted build with `CONFIG_VIDEO_SUN8I_DEINTERLACE=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/sun8i-di.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/sun8i-di.c

Purpose: implements a V4L2 memory-to-memory driver for the Allwinner sun8i deinterlace unit with scaling support for NV12/NV21 input and output.

Important APIs and functions: module entry is `module_platform_driver(deinterlace_driver)`. Key paths include `deinterlace_device_run`, `deinterlace_irq`, `deinterlace_init`, V4L2 format ioctls, vb2 queue callbacks, `deinterlace_open`, `deinterlace_release`, platform probe/remove, and runtime resume/suspend.

Control flow: open allocates a per-file `deinterlace_ctx`, initializes default interlaced output and progressive capture formats, and creates a V4L2 M2M context. Streaming the output queue resumes PM and allocates two coherent flag buffers. The mem2mem scheduler runs only when at least one source and two destination buffers are ready. `device_run` programs input/output DMA addresses, line strides, format selection, previous-frame reference, scaling factors, neutral coefficients, field count, interrupts, and starts writeback. The IRQ handles writeback completion, marks each destination buffer done, alternates fields for a second pass when needed, stores the latest source as previous reference, completes the prior previous buffer, and finishes the M2M job.

State and persistence: per-context state includes source/destination formats, two flag buffers, previous source buffer, first/current field, and abort flag. Device state includes V4L2 device, video node, M2M scheduler, MMIO base, clocks, reset, and mutex. Hardware state is reinitialized on runtime resume and per job.

Dependencies and integration points: depends on V4L2 mem2mem core, videobuf2 DMA-contig, platform IRQ/MMIO resources, runtime PM, common clocks, reset, and coherent DMA. The compatible is `allwinner,sun8i-h3-deinterlace`.

Risks: two destination buffers are required for job readiness, reflecting field processing; userspace with too few capture buffers will stall. The previous-frame buffer is retained across jobs and must be returned on queue cleanup. Coefficient poll timeout result is ignored. Only NV12/NV21 are exposed. `kzalloc_obj` is used instead of the common `kzalloc(sizeof(*ctx), ...)`, so build environment support for that helper is assumed in this tree.

Test signals: v4l2-compliance for mem2mem ioctls, NV12/NV21 conversion/deinterlacing with two capture buffers, interlaced field order TB/BT, resize paths, abort/streamoff cleanup, runtime PM balancing, and IRQ writeback error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/sun8i-di.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/sun8i-di.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/sun8i-di.h

Purpose: defines the sun8i deinterlace register map, format constants, size limits, and core per-context/per-device state structures.

Important APIs and types: contains many `DEINTERLACE_*` register offsets and bit helpers for module enable, frame control, bypass, buffers, strides, formats, interrupts, thresholds, scaling coefficients, and sizes. Defines `struct deinterlace_ctx` and `struct deinterlace_dev`.

Control flow: the implementation uses these constants to program one deinterlace job and runtime initialization. Context and device structures are the bridge between file handles, M2M scheduling, vb2 buffers, and platform resources.

State and persistence: `deinterlace_ctx` persists per open file and tracks formats, flag buffers, previous buffer, field state, and aborting. `deinterlace_dev` persists per platform device and owns V4L2, video, M2M, MMIO, clocks, reset, and mutex state.

Dependencies and integration points: includes V4L2 device, mem2mem, videobuf2 V4L2/DMA-contig, and platform-device headers. It is private to `sun8i-di.c`.

Risks: register constants are numerous and mostly unvalidated at compile time. Min/max dimensions and NV12/NV21-only assumptions are baked into the implementation. Buffer address registers take full DMA addresses without high-register support, so platform DMA address width must match hardware capability.

Test signals: compile coverage plus hardware runs that exercise buffer addresses, field counters, writeback strides, and scaling coefficient registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-di/sun8i-di.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/Kconfig

Purpose: defines the build option for the Allwinner DE2 rotation V4L2 mem2mem driver.

Important APIs and symbols: `VIDEO_SUN8I_ROTATE` is a tristate depending on V4L mem2mem drivers, video, sunxi or compile-test, common clock, reset, OF, and PM. It selects videobuf2 DMA-contig and `V4L2_MEM2MEM_DEV`.

Control flow: selecting the symbol builds the composite `sun8i-rotate` module from core and format-table objects.

State and persistence: build configuration only.

Dependencies and integration points: exposes a standalone rotation/copy engine through V4L2 M2M.

Risks: runtime support depends on clocks, reset, IRQ, and compatible `allwinner,sun8i-a83t-de2-rotate`.

Test signals: Kconfig visibility, module build, and video-node registration on matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/Makefile

Purpose: links the sun8i rotate driver from its core implementation and format table.

Important APIs and entries: `sun8i-rotate-y` includes `sun8i_rotate.o` and `sun8i_formats.o`; `obj-$(CONFIG_VIDEO_SUN8I_ROTATE)` builds `sun8i-rotate.o`.

Control flow: kbuild links both objects into one module or built-in object.

State and persistence: no runtime state.

Dependencies and integration points: matches the split between register/V4L2 logic and reusable format lookup/enumeration.

Risks: adding formats only in one file is safe, but splitting more helpers requires Makefile updates.

Test signals: targeted build with `CONFIG_VIDEO_SUN8I_ROTATE=m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i-formats.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i-formats.h

Purpose: declares rotate-driver pixel-format metadata and lookup/enumeration helpers.

Important APIs and types: defines `ROTATE_FLAG_YUV`, `ROTATE_FLAG_OUTPUT`, `struct rotate_format`, `rotate_find_format`, and `rotate_enum_fmt`.

Control flow: the rotate implementation uses lookup to validate formats, compute pitches/plane offsets, and program hardware format codes. Enumeration uses the output flag to restrict capture formats.

State and persistence: no mutable state; format data lives in the C file's static table.

Dependencies and integration points: includes `linux/videodev2.h` for FourCC definitions. It is the private API between `sun8i_formats.c` and `sun8i_rotate.c`.

Risks: flags encode policy as well as hardware capability; incorrect flags can expose unsupported capture formats or hide valid ones.

Test signals: format enumeration through V4L2 ioctls and static compile coverage for table/helper signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i-formats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i-rotate.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i-rotate.h

Purpose: defines the sun8i DE2 rotation register map, hardware format constants, size limits, and per-context/per-device state structures.

Important APIs and constants: includes global control, interrupt, input/output format, size, pitch, address registers, burst/mode constants, hardware format codes, `ROTATE_SIZE`, min/max dimensions, `struct rotate_ctx`, and `struct rotate_dev`.

Control flow: `sun8i_rotate.c` uses these definitions to configure one M2M rotation job, process interrupts, and manage runtime PM resources.

State and persistence: `rotate_ctx` stores per-file source/destination formats, control handler, hflip/vflip/rotate controls. `rotate_dev` stores platform-wide V4L2/video/M2M objects, MMIO base, clocks, reset, and mutex.

Dependencies and integration points: includes V4L2 controls, device, mem2mem, videobuf2, DMA-contig, and platform-device headers.

Risks: high address registers are always written as zero in the implementation, so DMA address width is a hardware/platform assumption. Rotation constants map directly to `rotate / 90`; control validation must stay aligned with that.

Test signals: register programming through real rotation jobs, 90/180/270-degree geometry validation, and high-DMA-address platform testing if applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i-rotate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i_formats.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i_formats.c

Purpose: provides the supported pixel-format table and lookup/enumeration helpers for the sun8i rotate mem2mem driver.

Important APIs and functions: exports `rotate_find_format` and `rotate_enum_fmt`. The static `rotate_formats` table maps V4L2 FourCC values to hardware format codes, plane counts, bytes-per-pixel values, horizontal/vertical subsampling, and policy flags.

Control flow: lookup linearly scans the table by FourCC. Enumeration linearly scans the table while optionally filtering for formats allowed on capture buffers through `ROTATE_FLAG_OUTPUT`.

State and persistence: immutable static format metadata only.

Dependencies and integration points: depends on V4L2 FourCC values and hardware format constants from `sun8i-rotate.h`. The rotate driver uses this metadata for validation, pitch/size calculations, address-plane layout, and capture-format derivation.

Risks: not all hardware formats are present; the file explicitly excludes `ROTATE_FORMAT_BGR565` and `ROTATE_FORMAT_VYUV`. Many YUV input formats lack `ROTATE_FLAG_OUTPUT`, so capture output is normalized to YUV420 for YUV sources. Incorrect bpp/subsampling metadata would corrupt plane offsets and DMA pitches.

Test signals: V4L2 format enumeration for output/capture, round-trip lookup for each listed format, image tests for RGB and YUV planar/semi-planar formats, and pitch/sizeimage verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i_formats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i_rotate.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i_rotate.c

Purpose: implements the Allwinner DE2 rotation unit as a V4L2 memory-to-memory device with format negotiation, rotation/flip controls, DMA address programming, IRQ completion, and runtime PM.

Important APIs and functions: module entry is `module_platform_driver(rotate_driver)`. Key functions include `rotate_device_run`, `rotate_irq`, format ioctls, `rotate_s_ctrl`, vb2 queue callbacks, `rotate_open`, `rotate_release`, platform probe/remove, and runtime resume/suspend.

Control flow: open allocates a per-file context, sets default ARGB32 source and matching capture format, creates an M2M context, installs hflip/vflip/rotate controls, and attaches the control handler. Output format changes validate and align dimensions and then recompute capture format; rotation control changes also recompute capture geometry and reject changes when the capture queue is busy. Streaming the output queue resumes runtime PM. Each M2M job programs global control with mode, flips, rotation, and burst length; programs input format, size, pitches, and plane addresses; programs output size, pitches, and addresses; enables finish IRQ; and starts the hardware. IRQ completion clears the finish flag, marks source and destination buffers done, and finishes the job.

State and persistence: per-context state includes source/destination formats, controls, and current transform values. Device state includes V4L2/video/M2M objects, MMIO base, bus/mod clocks, reset, and mutex. Hardware state is per job and reset/powered by runtime PM.

Dependencies and integration points: depends on V4L2 mem2mem, V4L2 controls/events, vb2 DMA-contig, format helpers from `sun8i_formats.c`, platform IRQ/MMIO, clocks, reset, and runtime PM. Compatible is `allwinner,sun8i-a83t-de2-rotate`.

Risks: `rotate_device_run` returns early on unexpected missing formats without completing the M2M job, though format validation should prevent this. High DMA address registers are zeroed. Capture format for YUV inputs is forced to YUV420, so userspace must handle format conversion semantics. Runtime PM is tied to output queue streaming only. `rotate_open` error cleanup after `rotate_setup_ctrls` failure frees the context without releasing a successfully initialized M2M context.

Test signals: v4l2-compliance for M2M and controls, rotation at 0/90/180/270, hflip/vflip combinations, RGB and YUV format jobs, capture geometry changes with busy queues, streamoff cleanup, IRQ completion, and runtime PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i_rotate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/Kconfig

Purpose: aggregates Synopsys media platform driver configuration and defines the DesignWare MIPI CSI-2 receiver option.

Important APIs and symbols: sources `drivers/media/platform/synopsys/hdmirx/Kconfig` and defines `VIDEO_DW_MIPI_CSI2RX`, a tristate for the Synopsys DesignWare MIPI CSI-2 Receiver. It depends on Rockchip or compile-test, `VIDEO_DEV`, `V4L_PLATFORM_DRIVERS`, PM, and common clock; it selects generic MIPI D-PHY helpers, media controller, V4L2 fwnode, and V4L2 subdevice API.

Control flow: Kconfig first includes the HDMI RX child config, then exposes the CSI-2 receiver option. Selecting the option causes the sibling Makefile to build `dw-mipi-csi2rx.o`.

State and persistence: build configuration only.

Dependencies and integration points: integrates a generic Synopsys CSI-2 bridge used on Rockchip SoCs with external C-PHY/D-PHY and downstream VICAP-style capture blocks.

Risks: the option is Rockchip-scoped despite being a Synopsys IP block; other SoC users need dependency updates. External PHY and downstream capture integration are required at runtime even though not expressed as direct Kconfig dependencies.

Test signals: menu visibility under Rockchip and `COMPILE_TEST`, module build, and media graph binding with external PHY and downstream capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/Makefile

Purpose: descends into Synopsys HDMI RX support and builds the DesignWare MIPI CSI-2 receiver object when enabled.

Important APIs and entries: `obj-y += hdmirx/` always descends into the HDMI RX child directory. `obj-$(CONFIG_VIDEO_DW_MIPI_CSI2RX) += dw-mipi-csi2rx.o` maps the Kconfig symbol to its object.

Control flow: kbuild evaluates child HDMI RX objects through that directory and conditionally compiles the CSI-2 receiver.

State and persistence: no runtime state.

Dependencies and integration points: mirrors the Synopsys Kconfig source relationship and links the DW CSI-2 receiver into the media platform build.

Risks: child directory traversal and Kconfig sourcing must remain synchronized. If `dw-mipi-csi2rx.c` is split, this Makefile must be updated.

Test signals: media platform build with `VIDEO_DW_MIPI_CSI2RX` enabled and disabled, plus HDMI RX child build traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/Makefile -->
