# subset-b-004226 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-jpeg.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-jpeg.c

## Purpose
`v4l2-jpeg.c` provides V4L2 JPEG helper data and a bounded JPEG header parser for kernel JPEG codec drivers. It exports standard Annex K quantization and Huffman reference tables, the zigzag scan order, and `v4l2_jpeg_parse_header()` for parsing marker segments up to the start of entropy-coded data.

## Important APIs, Types, And Functions
The public exports are the reference table arrays, `v4l2_jpeg_zigzag_scan_index`, and `v4l2_jpeg_parse_header(void *buf, size_t len, struct v4l2_jpeg_header *out)`. Internally, `struct jpeg_stream` tracks the current and end byte pointers. `jpeg_get_byte()`, `jpeg_get_word_be()`, and `jpeg_skip()` enforce buffer bounds. Segment parsers fill `struct v4l2_jpeg_frame_header`, `struct v4l2_jpeg_scan_header`, `struct v4l2_jpeg_reference`, restart interval, and APP14 transform metadata.

## Control Flow
`v4l2_jpeg_parse_header()` verifies an initial SOI marker, initializes DHT/DQT counters and APP14 state, then loops through markers with `jpeg_next_marker()`. Baseline and extended sequential SOF markers are accepted; progressive, lossless, arithmetic, and unsupported SOF/DAC/TEM markers return `-EINVAL`. DHT and DQT segments are either referenced and skipped or parsed into caller-provided table arrays. DRI updates the restart interval. APP14 parses Adobe transform data if present. SOS records the scan header, sets `ecs_offset`, and returns, deliberately stopping before entropy-coded data.

## State And Persistence
The parser is stateless outside the caller-owned output structure. Segment references point directly into the supplied buffer, so callers must keep that buffer alive while using returned `start` pointers. The file has no persistent storage, no global mutable state, and no hardware interaction.

## Dependencies And Integration Points
The file depends on `<media/v4l2-jpeg.h>` for output structures and constants, Linux unaligned big-endian helpers, and kernel errno conventions. It integrates with JPEG mem2mem/stateless codec drivers that need to validate JPEG streams and program hardware with frame size, subsampling, quantization, Huffman, and restart data.

## Risks And Test Signals
Important risks are malformed length handling, table count wrapping into the four-reference arrays, reliance on SOF precision before DQT parsing, and rejecting valid JPEG variants outside the supported baseline/extended-sequential subset. Good tests include truncated buffers at every marker boundary, invalid SOF/DQT/DHT lengths, grayscale and 4-component subsampling cases, APP14 Adobe transform extraction, DRI parsing, DHT/DQT skip mode with NULL table arrays, and ensuring `ecs_offset` points just after SOS header parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-jpeg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-mc.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-mc.c

## Purpose
`v4l2-mc.c` contains V4L2 helpers for media-controller graph construction, fwnode-based link creation, media-source enable/disable callbacks, vb2 source activation, and legacy pipeline power management.

## Important APIs, Types, And Functions
Exports include `v4l2_mc_create_media_graph()`, `v4l_enable_media_source()`, `v4l_disable_media_source()`, `v4l_vb2q_enable_media_source()`, `v4l2_create_fwnode_links_to_pad()`, `v4l2_create_fwnode_links()`, `v4l2_pipeline_pm_get()`, `v4l2_pipeline_pm_put()`, and `v4l2_pipeline_link_notify()`. The file operates on `struct media_device`, `struct media_entity`, `struct media_link`, `struct video_device`, `struct vb2_queue`, and `struct v4l2_subdev`.

## Control Flow
`v4l2_mc_create_media_graph()` scans entities by function, discovers tuners, IF decoders, analog decoders, connectors, video/VBI/software-radio I/O nodes, and camera sensors, then creates enabled pad links for webcam or analog-TV style graphs. Fwnode helpers iterate source endpoints, map local source pads and remote sink pads, skip existing links, and call `media_create_pad_link()`. Source enable/disable helpers serialize through `mdev->graph_mutex` and call media-device callbacks when present. Pipeline PM helpers walk the graph, count open video nodes, and call subdev `core.s_power` on 0-to-nonzero and nonzero-to-0 transitions.

## State And Persistence
The persistent state modified here is in media-controller graph objects: pad links, entity `use_count`, video pipeline fields, and optional device-specific source ownership. No data is stored outside kernel objects. Graph and power changes are protected by `graph_mutex`, while graph walks use `mdev->pm_count_walk`.

## Dependencies And Integration Points
This file depends on the media entity/link API, V4L2 file handles, V4L2 subdev calls, videobuf2 queues, fwnode graph helpers, and optional media-device callbacks. It is used by bridge drivers that expose media-controller topology without manually wiring every common link pattern.

## Risks And Test Signals
Graph construction is sensitive to correct entity functions, pad flags, and `PAD_SIGNAL_*` annotations. Pipeline PM can miscount if link notifications and open/close paths are not paired. Tests should build representative webcam, tuner+IF+decoder, connector, VBI, and SDR graphs; verify duplicate fwnode links are skipped; exercise source enable contention returning `-EBUSY`; and validate power rollback when a subdev `s_power(1)` fails partway through a graph walk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-mc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-mem2mem.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-mem2mem.c

## Purpose
`v4l2-mem2mem.c` implements the V4L2 memory-to-memory framework for drivers that process OUTPUT buffers into CAPTURE buffers through videobuf2. It provides context scheduling, ready-buffer queues, ioctl and file-operation helpers, request API queueing, draining semantics, and optional media-controller topology registration.

## Important APIs, Types, And Functions
The central private type is `struct v4l2_m2m_dev`, which stores current context, job queue, spinlock, work item, operation callbacks, kref, and optional media entities. Public helpers include queue accessors, ready-buffer operations, `v4l2_m2m_try_schedule()`, `v4l2_m2m_job_finish()`, `v4l2_m2m_buf_done_and_job_finish()`, suspend/resume, vb2 ioctl wrappers, mmap/poll helpers, encoder/decoder command helpers, `v4l2_m2m_init()`, `v4l2_m2m_ctx_init()`, `v4l2_m2m_ctx_release()`, `v4l2_m2m_buf_queue()`, and metadata/request helpers.

## Control Flow
Drivers initialize a device with `v4l2_m2m_init()` and a per-file context with `v4l2_m2m_ctx_init()`. Buffer queue callbacks add vb2 buffers to per-queue ready lists. `v4l2_m2m_try_schedule()` verifies streaming state, abort flags, source/destination availability, held capture timestamp rules, stopped state, and optional `job_ready()`, then queues one job per context. `v4l2_m2m_try_run()` selects the first queued context if no job is active and invokes driver `device_run()`. Completion removes the context from the job queue, wakes waiters, clears current context, and schedules the next run through workqueue context.

## State And Persistence
State lives in `struct v4l2_m2m_ctx` and queue contexts: ready lists, ready counts, streaming/draining/stopped flags, last source buffer, next-last capture marker, `new_frame`, and job flags `TRANS_QUEUED`, `TRANS_RUNNING`, and `TRANS_ABORT`. Device-wide state tracks `curr_ctx`, `job_queue`, paused state, media entities, and kref lifetime. Spinlocks protect ready lists and job state; optional queue mutexes protect file-operation paths.

## Dependencies And Integration Points
The framework integrates with videobuf2, V4L2 file handles/events, media requests, video device ioctls, media-controller entities, and driver callbacks in `struct v4l2_m2m_ops`. CAPTURE MMAP offsets are shifted by `DST_QUEUE_OFF_BASE` to distinguish the two queues. Optional media-controller registration creates source, processing, sink, and interface entities with immutable enabled links.

## Risks And Test Signals
Key risks are races between streamoff, job completion, request queueing, held capture buffers, and draining LAST-buffer handling. Tests should cover dual-queue streamon/order variations, nonblocking poll results, CAPTURE request rejection, MMAP offset adjustment for single and multiplanar buffers, streamoff during running and queued jobs, suspend waiting for current completion, encoder/decoder STOP/START state, stateless decoder FLUSH releasing held buffers, media-controller registration rollback, and kref release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-mem2mem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-spi.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-spi.c

## Purpose
`v4l2-spi.c` provides helper routines for V4L2 subdevices implemented as SPI devices. It mirrors the older I2C helper pattern for initializing, dynamically creating, registering, and unregistering SPI-backed subdevs.

## Important APIs, Types, And Functions
Exports are `v4l2_spi_subdev_init()`, `v4l2_spi_new_subdev()`, and `v4l2_spi_subdev_unregister()`. They operate on `struct v4l2_subdev`, `struct spi_device`, `struct spi_controller`, `struct spi_board_info`, and `struct v4l2_device`.

## Control Flow
`v4l2_spi_subdev_init()` calls `v4l2_subdev_init()`, marks the subdev as SPI, copies the SPI driver's module owner, stores the SPI device in subdev private data, stores the subdev in SPI driver data, and formats a subdev name from driver and device names. `v4l2_spi_new_subdev()` optionally requests the module named by `modalias`, creates a device with `spi_new_device()`, verifies a bound driver, takes the module reference, retrieves the subdev from driver data, registers it with the V4L2 device, then drops the temporary module reference. On failure it unregisters the SPI device. `v4l2_spi_subdev_unregister()` unregisters only board-created SPI devices without firmware nodes.

## State And Persistence
State is the bidirectional association between SPI device and V4L2 subdev, plus module reference counts during registration. No persistent configuration is stored by this helper; it delegates lifetime to SPI core and V4L2 device registration.

## Dependencies And Integration Points
The file depends on SPI core APIs, V4L2 common/device/subdev helpers, and module loading. It is used by bridge drivers that instantiate SPI peripheral subdevices from board info instead of firmware-described devices.

## Risks And Test Signals
Risks include NULL driver pointers after device creation, module reference imbalance, unregistering firmware-owned devices, and assuming the SPI driver set its drvdata to a subdev during probe. Tests should cover modalias autoload success/failure, driver-bound and unbound `spi_new_device()` results, `__v4l2_device_register_subdev()` failure cleanup, and unregister behavior for OF/fwnode versus board-info devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-subdev-priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-subdev-priv.h

## Purpose
`v4l2-subdev-priv.h` is a small private header for V4L2 subdevice core internals. It exposes privacy LED acquire/release helpers to core files without making them part of the public media header API.

## Important APIs, Types, And Functions
It declares `int v4l2_subdev_get_privacy_led(struct v4l2_subdev *sd)` and `void v4l2_subdev_put_privacy_led(struct v4l2_subdev *sd)`. The implementation is in `v4l2-subdev.c`.

## Control Flow
There is no runtime control flow in this header. Including files can call the get helper during subdev setup and the put helper during teardown. The implementation acquires an LED named `privacy`, disables user sysfs control while owned, and restores access on release when LED class support is reachable.

## State And Persistence
The declared helpers operate on `sd->privacy_led`. The header itself owns no state and stores no data.

## Dependencies And Integration Points
The header assumes `struct v4l2_subdev` is visible to including code through surrounding V4L2 headers. It is intentionally private to `drivers/media/v4l2-core`.

## Risks And Test Signals
The main risk is accidental public use or include-order breakage if included without a visible `struct v4l2_subdev` declaration. Build coverage with LED class enabled, modular, and disabled configurations is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-subdev-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-subdev.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-subdev.c

## Purpose
`v4l2-subdev.c` implements the V4L2 subdevice core: subdev devnode file operations, ioctl dispatch, pad-operation validation wrappers, active/try state allocation, media-controller link validation, routing and stream-state helpers, event notification, initialization, cleanup, and privacy LED ownership.

## Important APIs, Types, And Functions
Important exports include `v4l2_subdev_call_wrappers`, `v4l2_subdev_fops`, `v4l2_subdev_link_validate_default()`, `v4l2_subdev_link_validate()`, state allocation/free/finalize/cleanup helpers, state accessors for format/crop/compose/interval, routing helpers, stream enable/disable helpers, `v4l2_subdev_s_stream_helper()`, frame-descriptor passthrough helpers, `v4l2_subdev_init()`, `v4l2_subdev_notify_event()`, `v4l2_subdev_is_streaming()`, and privacy LED get/put. Internal `struct v4l2_subdev_stream_config` stores per-pad/per-stream format, crop, compose, interval, and enabled state.

## Control Flow
When the subdev API is enabled, `subdev_open()` allocates a file-handle state, initializes a V4L2 fh, pins the media-device owner, and calls internal open hooks. Ioctls enter through `video_usercopy()`, take the video-device lock, select active or try state based on command and `which`, lock that state, and dispatch controls, events, pad format/selection/frame interval, EDID, DV timings, standards, routing, and client capabilities. Pad wrapper functions validate `which`, pad index, stream availability, and state before calling driver ops. Link validation compares stream masks and source/sink formats, delegating to video-device validation when needed. Stream helpers validate source pads, stream masks, duplicate enable/disable, then call modern `.enable_streams()`/`.disable_streams()` or legacy `.s_stream()` fallback.

## State And Persistence
Persistent runtime state is held in `struct v4l2_subdev`: active state, optional shared state lock, enabled pads, legacy `s_stream_enabled`, event flags, privacy LED pointer, async endpoint list, and media entity metadata. `struct v4l2_subdev_state` owns legacy pad configs or streams API routing/config arrays. State allocation may call driver `internal_ops->init_state()`. Cleanup frees active state and async endpoint records. Privacy LED ownership disables sysfs access while held and toggles brightness during streaming.

## Dependencies And Integration Points
The file depends on V4L2 controls, events, file handles, ioctl helpers, media-controller entities and pads, fwnode matching, LED class support, and driver-supplied subdev ops. It forms the main integration layer between userspace subdev devnodes, bridge drivers, sensor drivers, routing-aware subdevs, and media graph validation.

## Risks And Test Signals
Risks cluster around ioctl permission checks, active versus try state locking, experimental streams API gating, route validation limits, stream enable/disable idempotency, and legacy `.s_stream()` compatibility. Tests should cover read-only devnodes rejecting active setters, stream-cap negotiation, routing copy-in/copy-out and validation restrictions, link validation with dangling sink streams and mismatched formats, state accessors under legacy and streams modes, privacy LED acquisition/release with LED class variants, event polling, compat ioctl delegation, and cleanup after partially initialized subdevs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-subdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-trace.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-trace.c

## Purpose
`v4l2-trace.c` instantiates and exports V4L2/videobuf2 tracepoints. Defining `CREATE_TRACE_POINTS` before including `<trace/events/v4l2.h>` creates the tracepoint storage.

## Important APIs, Types, And Functions
The file exports tracepoint symbols `vb2_v4l2_buf_done`, `vb2_v4l2_buf_queue`, `vb2_v4l2_dqbuf`, and `vb2_v4l2_qbuf` with `EXPORT_TRACEPOINT_SYMBOL_GPL()`.

## Control Flow
There are no callable functions. Build inclusion creates tracepoints, and the export macros make them available to GPL modules and tracing infrastructure.

## State And Persistence
Tracepoint state is managed by the kernel tracing subsystem. This file does not store device state or alter V4L2 behavior unless tracing clients subscribe to the exported events.

## Dependencies And Integration Points
It includes V4L2 common/file-handle and videobuf2 V4L2 headers so the trace event definitions have the required types. It integrates with ftrace/perf/eBPF and any in-kernel modules that attach to exported tracepoints.

## Risks And Test Signals
Risks are mostly build-time: duplicate `CREATE_TRACE_POINTS`, missing type definitions, or tracepoint ABI churn. Test signals are successful media subsystem builds, visible trace events under tracing filesystems, and trace output when qbuf/dqbuf/buf_queue/buf_done paths run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-vp9.c -->
# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-vp9.c

## Purpose
`v4l2-vp9.c` provides VP9 probability tables and helper algorithms for stateless V4L2 VP9 decoders. It translates userspace-parsed compressed-header deltas and hardware/software symbol counts into updated VP9 frame contexts.

## Important APIs, Types, And Functions
Exports include keyframe probability tables, `v4l2_vp9_default_probs`, `v4l2_vp9_fw_update_probs()`, `v4l2_vp9_reset_frame_ctx()`, `v4l2_vp9_adapt_coef_probs()`, `v4l2_vp9_adapt_noncoef_probs()`, and `v4l2_vp9_seg_feat_enabled()`. Core internal helpers include `fastdiv()`, `update_prob()`, update routines for each compressed-header probability family, `merge_prob()`, non-coefficient merge variants, and coefficient adaptation loops.

## Control Flow
Firmware update flow starts with optional transform-size probabilities, updates coefficient probabilities up to the selected transform mode, then updates skip probabilities. For key or intra-only frames it stops there. Inter frames continue through inter mode, interpolation filter when switchable, is-inter, reference mode, y mode, partition, and motion-vector probabilities. Reset flow copies default probabilities into all or selected frame contexts depending on key/intra/error-resilient flags and reset mode, then returns the active context index. Adaptation flow merges observed symbol counts into coefficient and non-coefficient probabilities using VP9 section 8.4 formulas without recursion.

## State And Persistence
The file has immutable exported default tables and mutates caller-provided `struct v4l2_vp9_frame_context` arrays. There is no global mutable state, no allocation, and no hardware access. Persistence of adapted contexts is the responsibility of the decoder driver and userspace control sequencing.

## Dependencies And Integration Points
The helpers depend on `<media/v4l2-vp9.h>` controls, frame context structures, compressed-header deltas, frame parameters, and symbol count structures. They are intended for stateless VP9 drivers that need kernel-side context maintenance around V4L2 controls.

## Risks And Test Signals
Risks include array-shape drift against UAPI structs, off-by-one errors in VP9 tree merge variants, divide approximation mistakes, incorrect high-precision motion-vector gating, and adapting contexts for frame types that should stop early. Tests should compare helper output with a reference VP9 probability implementation for key, intra-only, error-resilient, inter, switchable interpolation, high-precision MV, all reset modes, empty counts, saturated counts, and segment feature bit checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-vp9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/memory/Kconfig

## Purpose
This Kconfig file defines the Linux memory-controller driver menu and configuration symbols for embedded DRAM, SRAM, external bus, static memory controller, memory fabric, and SoC-specific memory-controller support.

## Important APIs, Types, And Functions
The top-level `menuconfig MEMORY` gates the menu. Symbols include generic `DDR`, platform drivers such as `ATMEL_EBI`, `BRCMSTB_DPFE`, `BRCMSTB_MEMC`, `TI_AEMIF`, `TI_EMIF`, `OMAP_GPMC`, `FSL_CORENET_CF`, `FSL_IFC`, `MVEBU_DEVBUS`, `JZ4780_NEMC`, `MTK_SMI`, `DA8XX_DDRCTL`, `PL353_SMC`, `RENESAS_RPCIF`, `STM32_FMC2_EBI`, `STM32_OMM`, plus `TI_EMIF_SRAM` and `FPGA_DFL_EMIF`. It sources Samsung and Tegra submenus.

## Control Flow
Kconfig evaluation first exposes the memory controller menu, then conditionally offers drivers according to architecture, OF, AMBA, SRAM, FPGA, HAS_IOMEM, and COMPILE_TEST dependencies. Several symbols select helper subsystems: `ATMEL_EBI` selects syscon and Atmel SMC MFD support; `TI_EMIF` selects `DDR`; `OMAP_GPMC` selects `GPIOLIB`; `RENESAS_RPCIF` selects regmap MMIO and reset controller.

## State And Persistence
The persistent output is kernel configuration state. These symbols determine which objects the Makefile compiles and which dependencies must be enabled. There is no runtime state in the file.

## Dependencies And Integration Points
It integrates with the kernel Kconfig system, architecture symbols, driver submenus, and the sibling Makefile. Help text describes user-visible purpose for each driver and constrains build coverage through `COMPILE_TEST`.

## Risks And Test Signals
Risks include missing dependencies causing randconfig build failures, over-restrictive dependencies hiding valid drivers, incorrect default selections, and stale help text. Test signals include `allyesconfig`, `allmodconfig`, architecture defconfigs, and randconfig builds across ARM, ARM64, MIPS, and COMPILE_TEST configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/Makefile -->
# sources/distributed-fs/ceph-client/drivers/memory/Makefile

## Purpose
This Makefile maps memory-controller Kconfig symbols to compiled objects and subdirectories. It also defines the special build rule for TI EMIF SRAM suspend code offsets.

## Important APIs, Types, And Functions
The main entries are `obj-$(CONFIG_...) += ...` assignments for each memory controller object or subdirectory. `ti-emif-sram-objs` combines `ti-emif-pm.o` and `ti-emif-sram-pm.o`. A generated header rule builds `ti-emif-asm-offsets.h` from `emif-asm-offsets.s` using `filechk`.

## Control Flow
Kbuild includes objects according to selected configuration symbols. `of_memory.o` is included only when `CONFIG_DDR=y` and `CONFIG_OF` is enabled, not when DDR is modular. Samsung and Tegra directories are descended into when their controller symbols are enabled. The TI EMIF SRAM object depends on generated assembly offsets, and the generated header is listed in `clean-files`.

## State And Persistence
Persistent build artifacts include object files, the generated `ti-emif-asm-offsets.h`, and intermediate `emif-asm-offsets.s`. The source Makefile itself has no runtime behavior.

## Dependencies And Integration Points
It integrates Kconfig decisions with Kbuild, the drivers/memory source tree, generated-offset infrastructure, and assembly PM code that needs C structure offsets.

## Risks And Test Signals
Risks include object names drifting from source files, missing composite-object members, generated header ordering failures, and `of_memory.o` unexpectedly absent for modular DDR builds. Test signals include clean and incremental builds for each memory-controller symbol, `make clean` removing generated offsets, and build coverage of Samsung/Tegra subdirectories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/atmel-ebi.c -->
# sources/distributed-fs/ceph-client/drivers/memory/atmel-ebi.c

## Purpose
`atmel-ebi.c` is the platform driver for Atmel/Microchip external bus interface controllers. It configures Static Memory Controller timings and modes for child devices described in device tree and restores those configurations on resume.

## Important APIs, Types, And Functions
Important types are `struct atmel_ebi`, `struct atmel_ebi_dev`, `struct atmel_ebi_dev_config`, and `struct atmel_ebi_caps`. The caps table provides available chip selects, optional EBI CSA register offset, syscon phandle name, and get/xlate/apply callbacks. Core functions include `atmel_ebi_xslate_smc_timings()`, `atmel_ebi_xslate_smc_config()`, `atmel_ebi_dev_setup()`, `atmel_ebi_dev_disable()`, `atmel_ebi_probe()`, and `atmel_ebi_resume()`.

## Control Flow
Probe allocates driver state, gets the EBI clock, resolves the `atmel,smc` syscon/regmap/layout/clock, optionally resolves the matrix or SFR regmap for EBICSA, reads address and size cell counts, and iterates available child nodes with `reg`. Each child setup validates chip-select entries against SoC capabilities, translates any `atmel,smc-*` timing/mode properties, applies config to all chip selects when present, reads back config into persistent per-child records, optionally clears EBICSA bits to attach the child to generic SMC logic, and records the child for resume. On child setup failure, the child device tree node is marked disabled before population.

## State And Persistence
Runtime state stores clocks, regmaps, SoC caps, and a list of configured child devices with read-back SMC configs. Hardware state is persisted in SMC and optional matrix/SFR registers. Resume replays saved per-chip-select configs. The driver is built in through `builtin_platform_driver_probe()`.

## Dependencies And Integration Points
The driver depends on OF, platform bus, syscon/regmap, Atmel SMC MFD helpers, Atmel matrix/SFR definitions, and child device population. It is selected by `CONFIG_ATMEL_EBI` and supports multiple AT91/SAMA5/SAM9X60 compatible strings through per-SoC caps.

## Risks And Test Signals
Risks include incomplete timing property groups, clock-rate conversion overflow or truncation, invalid `reg` cell parsing, leaking enabled SMC clocks on probe errors after enable, incorrect EBICSA bit handling, and resume replay after partial child setup. Tests should cover device trees with single and multiple chip selects, absent versus complete SMC properties, all bus widths/page modes/read-write modes, invalid chip selects, SAMA5 HSMC versus AT91 SMC paths, probe deferral/error paths, and suspend/resume register restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/atmel-ebi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/brcmstb_dpfe.c -->
# sources/distributed-fs/ceph-client/drivers/memory/brcmstb_dpfe.c

## Purpose
`brcmstb_dpfe.c` is a Broadcom STB DDR PHY Front End platform driver. It loads or verifies firmware for a DCPU inside the DDR PHY, exchanges mailbox commands with that firmware, and exposes DRAM information such as refresh and mode-register data through sysfs.

## Important APIs, Types, And Functions
Important types are `struct dpfe_firmware_header`, temporary `struct init_data`, `struct dpfe_api`, and `struct brcmstb_dpfe_priv`. API tables describe legacy v2, new v2, and v3 command layouts and sysfs attribute groups. Core functions include DCPU enable/disable helpers, `__send_command()`, firmware verification/write/checksum helpers, `brcmstb_dpfe_download_firmware()`, sysfs show/store methods, `brcmstb_dpfe_probe()`, remove, and resume.

## Control Flow
Probe maps named resources `dpfe-cpu`, `dpfe-dmem`, and `dpfe-imem`, selects the API table from OF match data, downloads firmware if needed, and creates API-specific sysfs groups. Firmware download first checks whether a running DCPU responds to GET_INFO. If not and a firmware filename is available, it requests firmware, validates magic, endian, sizes, and checksum, disables the DCPU, clears and writes DMEM/IMEM, verifies by reading back, then enables the DCPU. Sysfs reads send commands through message RAM and mailboxes, validate response checksums, then format version, refresh, vendor, or v3 DRAM data.

## State And Persistence
Driver state holds MMIO bases, selected API, device pointer, and a mutex. Hardware state includes DCPU reset/clock bits, mailbox registers, message RAM, DCPU IMEM/DMEM, and firmware execution state. Sysfs writes to `dpfe_refresh` update the firmware-provided interval field for API v2-style data. Resume reruns firmware download/verification.

## Dependencies And Integration Points
The driver depends on platform resources, OF match data, firmware loader, relaxed MMIO accessors, sysfs device attributes, mutex serialization, and Broadcom-compatible strings. It is built from `CONFIG_BRCMSTB_DPFE` and uses firmware `dpfe.bin` only for the old API path; newer APIs expect boot firmware to preload DCPU firmware.

## Risks And Test Signals
Risks include mailbox timeout handling, checksum index trust from firmware responses, endian conversion mistakes, firmware blob layout mismatches, stale DCPU firmware on resume, invalid response pointers for old APIs, and sysfs writes racing with reads. Tests should cover all OF compatibles/API tables, missing resources, missing firmware with probe defer, BE and LE firmware images, invalid magic/size/checksum, mailbox timeout/error codes, sysfs output formatting for v2 and v3, refresh writes, remove cleanup, and resume after DCPU reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/brcmstb_dpfe.c -->
