# subset-b-004173 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_vout.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_vout.c

Purpose: Implements the legacy V4L2 video-output driver for TI OMAP DSS video overlays. It exposes one or two `/dev/video*` TX nodes backed by OMAP video overlay planes, accepts vb2 contiguous output buffers or dmabufs, programs DSS overlay position/format/scaling/rotation, and advances queued frames on display sync interrupts.

Important APIs/functions: `omap_vout_try_format()` clamps output dimensions to 2..1280 by 2..720 and normalizes pixel format/stride. `video_mode_to_dss_mode()` maps V4L2 RGB/YUV formats to DSS color modes. `omapvid_setup_overlay()`, `omapvid_init()`, and `omapvid_apply_changes()` translate the current V4L2 crop/window/rotation state into `omap_overlay_info`, then call DSS manager `apply()`. The V4L2 ioctl table covers format, overlay window, framebuffer blending/keying, selection crop, output enumeration, streaming, events, and vb2 buffer ioctls. `omap_vout_s_ctrl()` handles rotate, vflip mirror, and background color controls. `omap_vout_vb2_start_streaming()` programs the first frame, registers the DISPC ISR, enables overlays, and initializes sequence/field state. `omap_vout_isr()` completes the previous vb2 buffer, dequeues the next frame, reprograms the overlay address plus crop offset, and applies changes.

Control flow: `late_initcall(omap_vout_init)` registers a probed platform driver after DSS is expected to exist. Probe initializes DSS compatibility, discovers displays/overlays/managers, enables attached displays, registers the parent V4L2 device, creates per-overlay video devices, and refreshes displays. Userspace then sets format/crop/window/control state while the vb2 queue is idle, queues buffers, and starts streaming. Streaming configures VRFB buffers when enabled, calculates crop offsets, registers sync interrupts, and advances frames on VSYNC or even/odd sync depending on display type. Stop unregisters the ISR, disables overlays, applies the manager state, and returns active/queued buffers with error.

State and persistence: Runtime state lives in `struct omap_vout_device`: V4L2 format/crop/window/framebuffer, controls, rotation/mirror, vb2 queue, current/next frame pointers, DMA queue, queued physical addresses, crop offsets, DSS mode, sequence, field tracking, and optional VRFB contexts. Driver-global module parameters select static VRFB allocation for video1/video2 and debug logging. There is no disk persistence; state is hardware, memory, and userspace-open-file lifetime only.

Dependencies/integration: Depends on OMAP DSS compatibility APIs, DISPC ISR registration, OMAP overlay/manager/display objects, videobuf2 DMA-contig, V4L2 core/ioctl/events/controls, and optional VRFB support from `omap_vout_vrfb.c`. It also relies on `omap_voutlib.c` for crop/window scaling helpers and memory allocation. Hardware assumptions include video overlays at DSS indexes 1/2, display timings from the attached panel, and DISPC interrupt names for LCD/LCD2/VENC/HDMI.

Risks and test signals: Buffer queue operations in `buf_queue()` are not locally spinlocked even though the ISR consumes `dma_queue` under `vbq_lock`; correctness depends on vb2 serialization and should be tested under rapid qbuf/streamoff. RGB24 is rejected with VRFB rotation, and rotation changes are not explicitly blocked while streaming except indirectly through control locking, so streaming-control tests matter. Interlaced VENC field logic has first-interrupt and field-id edge cases. Probe assumes `pdev->num_resources` maps to video devices. Test signals include format/crop/window ioctl clamping, dmabuf/mmap streaming, VSYNC frame sequence increments, streamoff buffer return, VRFB and non-VRFB builds, chromakey/global-alpha manager programming, display detach or missing driver, and suspend/removal cleanup through `video_unregister_device()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_vout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_vout_vrfb.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_vout_vrfb.c

Purpose: Provides the optional VRFB rotation/mirroring backend for the OMAP V4L2 output driver. It allocates VRFB contexts and shadow buffers, copies user output frames into VRFB-tiled memory with an interleaved DMA transfer, exposes the rotated physical address to DSS, and computes crop offsets compatible with VRFB alignment.

Important APIs/functions: `omap_vout_setup_vrfb_bufs()` requests four VRFB contexts, sizes worst-case 1280x720 shadow buffers to 32-pixel tiles, requests an interleaved DMA channel, allocates a DMA template, initializes the wait queue, and optionally preallocates all buffers. `omap_vout_vrfb_buffer_setup()` caps buffer count to `VRFB_NUM_BUFS`, lazily allocates hidden buffers, and calls `omap_vrfb_setup()` with YUV awareness. `omap_vout_prepare_vrfb()` builds a `dma_interleaved_template` from the vb2 DMA-contig plane into the 0-degree VRFB address, waits for `omap_vout_vrfb_dma_tx_callback()`, checks `dma_async_is_tx_complete()`, and stores the address for the requested rotation view. `omap_vout_calculate_vrfb_offset()` derives `cropped_offset`, `ps`, `vr_ps`, and `line_length` for all rotation/mirror combinations.

Control flow: The main driver calls setup during video device initialization when DSS generation supports VRFB. During queue setup, rotation/mirroring triggers allocation/setup of hidden buffers. Each buffer prepare copies the source frame into VRFB before it can be displayed. During streaming, the main ISR uses `queued_buf_addr[index] + cropped_offset`, where this file supplies both the rotated base address and the crop offset.

State and persistence: State is stored in `struct omap_vout_device`: four `struct vrfb` contexts, `smsshado_*` virtual/physical shadow buffer arrays, `smsshado_size`, `vrfb_static_allocation`, `queued_buf_addr[]`, and `struct vid_vrfb_dma` channel/template/wait/status fields. No persistent storage exists.

Dependencies/integration: Integrates with OMAP VRFB APIs, Linux DMAengine interleaved DMA, `vb2_dma_contig_plane_dma_addr()`, `omap_vout_alloc_buffer()`/`free_buffer()`, and rotation helpers from `omap_voutdef.h`. It is compiled only when `CONFIG_VIDEO_OMAP2_VOUT_VRFB` enables the header prototypes.

Risks and test signals: `req_status` is only set to allocated if the request path sets it correctly; tests should verify behavior when no DMA channel is available, because `omap_vout_prepare_vrfb()` dereferences channel/template for rotated buffers. Timeouts terminate DMA and fail the buffer. Offset math is fragile for YUV virtual pixel size, mirroring, crop edges, and 90/270 rotations. Static allocation failures must release all contexts. Test rotated YUYV/UYVY/RGB565/RGB32 buffers, odd crop rejection upstream, partial mmap buffer allocation with `startindex`, DMA timeout/error injection, unload cleanup, and non-VRFB builds through the stub header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_vout_vrfb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_vout_vrfb.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_vout_vrfb.h

Purpose: Declares the VRFB support interface consumed by `omap_vout.c` and supplies no-op stubs when VRFB support is not built. This keeps the main video-output driver source mostly independent of the optional rotation backend.

Important APIs/types: With `CONFIG_VIDEO_OMAP2_VOUT_VRFB`, the header declares `omap_vout_free_vrfb_buffers()`, `omap_vout_setup_vrfb_bufs()`, `omap_vout_release_vrfb()`, `omap_vout_vrfb_buffer_setup()`, `omap_vout_prepare_vrfb()`, and `omap_vout_calculate_vrfb_offset()`. Without the option, static inline stubs return success or do nothing.

Control flow: The main driver calls these hooks during device setup, vb2 queue setup, buffer prepare, crop-offset calculation, and cleanup. The stub path makes those call sites compile and execute as simple non-rotation behavior.

State and persistence: The header owns no state. It operates on `struct omap_vout_device` fields defined in `omap_voutdef.h` and only controls whether external functions or stubs are linked.

Dependencies/integration: Depends on prior visibility of `struct omap_vout_device`, `struct platform_device`, and `struct vb2_buffer`. It is tightly paired with `omap_vout_vrfb.c` and the Kconfig symbol used by the OMAP2/OMAP3 video-output build.

Risks and test signals: Stub success means call sites must independently gate rotation support via `rotation_type`; otherwise unsupported rotation paths can appear to succeed. Build-test both `CONFIG_VIDEO_OMAP2_VOUT_VRFB=y/m` and disabled configurations, including compilation units that include this header before full type definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_vout_vrfb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutdef.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutdef.h

Purpose: Defines shared constants, state structures, enums, and inline helpers for the OMAP V4L2 output driver and its VRFB/library helpers.

Important APIs/types: Size and capability constants cover pixel bytes-per-pixel, tile size, max video devices/overlays/displays/managers, default/min/max dimensions, VRFB transfer timeout, number of VRFB buffers, and maximum buffer size. `enum dma_channel_state`, `enum dss_rotation`, and `enum vout_rotaion_type` describe DMA allocation, DSS rotation encoding, and whether VRFB rotation is available. `struct vid_vrfb_dma` holds DMAengine channel/template/status/wait state. `struct omapvideo_info` binds a vout to overlays and rotation type. `struct omap2video_device` is the parent V4L2/DSS device aggregate. `struct omap_vout_buffer` wraps `vb2_v4l2_buffer`. `struct omap_vout_device` is the central per-video-node state object. Inline helpers convert vb2 buffers and answer/transform rotation+mirror state.

Control flow: The structures are allocated in `omap_vout_create_video_devices()`, populated during setup/probe, mutated by ioctls, consumed by vb2 callbacks, and read from the DISPC ISR. Rotation helpers drive both DSS overlay programming and VRFB offset/address selection.

State and persistence: All state is in memory and associated with the platform driver lifetime. `struct omap_vout_device` stores both userspace-visible V4L2 state and hardware-private details such as VRFB contexts, physical addresses, line length, field tracking, ISR handle, and frame queue pointers.

Dependencies/integration: Pulls in videobuf2 DMA-contig, V4L2 controls, OMAP DSS, OMAP VRFB, and DMAengine types. It is included by the main driver, VRFB backend, and helper library.

Risks and test signals: The misspelled `vout_rotaion_type` is ABI-internal but sticky. Fixed array sizes must match DSS discovery limits and `pdev->num_resources`; overflow checks live elsewhere. Rotation/mirror helper behavior reverses rotations under mirroring and should be covered for all four angles. Tests should focus on structure initialization, queue cleanup, VRFB disabled builds, and field interactions between ISR and streamoff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutlib.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutlib.c

Purpose: Implements helper routines for OMAP V4L2 output crop/window negotiation, default format-dependent layout, contiguous buffer allocation, and DSS generation detection.

Important APIs/functions: `omap_vout_default_crop()` centers the largest even crop that fits both source image and framebuffer. `omap_vout_try_window()` clips a requested overlay window to display bounds, enforces even dimensions, clears clips/bitmap, and rejects empty rectangles. `omap_vout_new_window()` applies a validated window and adjusts crop size for OMAP24xx/34xx scaling limits. `omap_vout_new_crop()` clips crop to source bounds, preserves resize ratios by adjusting `win`, enforces OMAP24xx 768-pixel vertical-resize line-buffer constraints and 2x/4x scaling limits, then updates crop. `omap_vout_new_format()` resets crop/window defaults after a format change. `omap_vout_alloc_buffer()` and `omap_vout_free_buffer()` allocate/free physically contiguous pages while marking pages reserved. `omap_vout_dss_omap24xx()` and `omap_vout_dss_omap34xx()` classify DSS versions.

Control flow: The main driver calls these helpers from format, overlay-window, and crop ioctls and from VRFB allocation paths. They are exported with `EXPORT_SYMBOL_GPL` for the geometric helpers, indicating reuse outside this source file.

State and persistence: Functions mutate caller-provided V4L2 rectangles, windows, pix formats, and framebuffer structs. Buffer allocation returns virtual and physical addresses to the caller; no module-global state is persisted.

Dependencies/integration: Depends on V4L2 structs, Linux page allocation and DMA mapping headers, and `omapdss_get_version()` from OMAP DSS. It encodes DSS-generation hardware limits used by `omap_vout.c`.

Risks and test signals: Integer division in scaling checks can hide near-threshold resize ratios, and crop/window clamping must avoid zero dimensions. Reserved-page allocation is legacy and should be stress-tested for allocation failure and cleanup. Test crop/window ioctls across negative origins, overlarge rectangles, OMAP24xx/34xx limits, RGB/YUV formats, and repeated VRFB static allocation/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutlib.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutlib.h

Purpose: Declares the shared helper API implemented by `omap_voutlib.c` for OMAP video-output geometry and buffer management.

Important APIs/functions: The header exposes crop/window helpers (`omap_vout_default_crop()`, `omap_vout_new_crop()`, `omap_vout_try_window()`, `omap_vout_new_window()`, `omap_vout_new_format()`), low-level contiguous page helpers (`omap_vout_alloc_buffer()`, `omap_vout_free_buffer()`), and DSS-version predicates (`omap_vout_dss_omap24xx()`, `omap_vout_dss_omap34xx()`).

Control flow: Included by the main vout driver and VRFB backend so both paths share the same crop/window rules and buffer allocation behavior.

State and persistence: No state is stored in the header. All functions operate on caller-provided structs or return allocation addresses.

Dependencies/integration: Requires V4L2 pix/framebuffer/window/rect types and `u32`/`bool` definitions from included translation units. Its declarations mirror the library’s exported GPL symbols plus non-exported allocation/version helpers used in-tree.

Risks and test signals: Because this header does not include the types it uses, compile order depends on includers already having V4L2 and kernel type headers. Build-test each includer and verify prototypes stay synchronized with `omap_voutlib.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap/omap_voutlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/Kconfig

Purpose: Defines configuration symbols for the TI OMAP3 camera ISP driver.

Important APIs/types: `VIDEO_OMAP3` is a tristate option labeled "OMAP 3 Camera support". It depends on platform V4L2 drivers, `VIDEO_DEV`, `I2C`, OMAP3+IOMMU or compile testing, common clock, and OF. It selects ARM DMA/IOMMU support when applicable, Media Controller, V4L2 subdev API, DMA-contig vb2, `MFD_SYSCON`, and `V4L2_FWNODE`. `VIDEO_OMAP3_DEBUG` is a bool that enables debug messages and depends on the main driver.

Control flow: Kconfig selection controls whether the `omap3-isp.o` composite module is built and whether the Makefile adds `-DDEBUG`.

State and persistence: Build-time configuration only. No runtime state.

Dependencies/integration: Integrates the driver with the Linux media subsystem, device tree endpoint parsing, common clocks, IOMMU DMA mapping, syscon, I2C-attached camera sensors, and vb2 DMA-contig buffers.

Risks and test signals: `COMPILE_TEST` broadens build coverage, but runtime still needs OMAP3 hardware, IOMMU, clocks, regulators, syscon, and OF graph endpoints. Test allmodconfig/allyesconfig compile paths, `VIDEO_OMAP3_DEBUG`, and real DT probe with dependent sensor subdevices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/Makefile

Purpose: Builds the OMAP3 ISP driver as one composite media driver object.

Important APIs/types: Adds `-DDEBUG` to compiler flags when `CONFIG_VIDEO_OMAP3_DEBUG` is enabled. Defines `omap3-isp-objs` as the core `isp.o` and `ispvideo.o` plus CSIPHY, CCP2, CSI2, CCDC, preview, resizer, statistics, H3A AEWB/AF, and histogram objects. Links `omap3-isp.o` under `obj-$(CONFIG_VIDEO_OMAP3)`.

Control flow: The object list controls module link order and ensures all internal subdevice implementations are part of the same module.

State and persistence: Build metadata only.

Dependencies/integration: Mirrors the Kconfig symbol and the internal module graph used by `isp.c`, which initializes and registers each submodule.

Risks and test signals: Missing an object breaks symbols referenced by `isp.c` or media graph creation. Test with `CONFIG_VIDEO_OMAP3=m` and `=y`, debug enabled/disabled, and compile-test configurations where OMAP headers are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/cfa_coef_table.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/cfa_coef_table.h

Purpose: Supplies static coefficient data for the OMAP3 ISP preview module’s CFA interpolation block. The file is an include fragment, not a standalone C header with guards.

Important APIs/types: Contains four brace-enclosed numeric coefficient arrays, each corresponding to a Bayer/CFA phase pattern expected by the including preview code. Values are byte-sized signed/encoded coefficients such as 244, 247, 250, 12, 27, 36, and 40 arranged in repeated filter kernels.

Control flow: There is no executable control flow. The including file inserts this initializer into a larger table and programs preview/CFA hardware from it.

State and persistence: Read-only compile-time table data. No mutable state or persistence.

Dependencies/integration: Integrated by `isppreview` code in the same driver directory. Table dimensions and order must match hardware register programming and the preview module’s Bayer pattern enumeration.

Risks and test signals: Because this is a raw initializer fragment, syntax and element count depend on the includer. Accidental reformatting or truncation can silently change image quality or overrun/underrun expected table size. Test by compiling the preview module, enabling raw Bayer preview paths, and comparing CFA output/color artifacts for all Bayer orders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/cfa_coef_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/gamma_table.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/gamma_table.h

Purpose: Provides the default gamma lookup table data used by the OMAP3 ISP preview engine for all color components. Like the CFA table, it is an include fragment containing initializer values.

Important APIs/types: The file is a monotonically nondecreasing sequence of 8-bit output values from 0 to 255, heavily repeated in high ranges, representing a default gamma curve.

Control flow: No executable logic. The including preview code embeds the values into a gamma table and writes them into ISP preview hardware or keeps them as default configuration data.

State and persistence: Read-only compile-time lookup data.

Dependencies/integration: Used by the OMAP3 ISP preview module. Its length and value range must match the hardware gamma table size and the structure initializer in the includer.

Risks and test signals: Raw initializer fragments are easy to break by adding guards or declarations that the includer does not expect. Image pipeline tests should validate default preview output, table upload, and no out-of-bounds reads/writes when the preview module indexes the table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/gamma_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isp.c

Purpose: Implements the core platform driver for the TI OMAP3 ISP media device. It owns hardware resource discovery, clock and power reference counting, interrupt dispatch, media graph registration, DT endpoint async binding, IOMMU attachment, xclk providers, pipeline stream sequencing, suspend/resume, and module-wide context save/restore.

Important APIs/functions: `omap3isp_flush()` forces posted register writes. XCLK helpers register two clock providers (`cam_xclka`, `cam_xclkb`) with rate-divider operations. `isp_enable_interrupts()` and `isp_isr()` enable and dispatch CSIA/CSIB, CCDC, preview, resizer, H3A, histogram, and SBL overflow events. `omap3isp_configure_bridge()` programs ISP bridge/lane shifter for parallel, CSI2, CCP2, or CSI2C input. `omap3isp_pipeline_set_stream()` walks media entities to enable/disable pipelines and statistics modules. `omap3isp_module_sync_idle()` and `omap3isp_module_sync_is_stopping()` synchronize module stop requests with IRQ completion. `omap3isp_get()`/`omap3isp_put()` reference-count clocks, interrupts, context, and reset recovery. `isp_probe()` maps MMIO, reads revision, sets resource offsets, attaches IOMMU, requests IRQ, initializes modules, registers entities, creates links, parses OF endpoints, and registers the async notifier.

Control flow: Probe allocates `struct isp_device`, reads `ti,phy-type` and syscon, maps MMIO areas, gets clocks/regulators, enables a minimal clock to read revision, resets hardware, registers xclks, computes per-block MMIO bases from revision maps, attaches IOMMU, requests IRQ, initializes all ISP submodules, registers internal media entities/video nodes, creates static internal links, parses external OF graph endpoints, registers the notifier, initializes core registers, and drops the initial runtime reference. When sensors bind, notifier callbacks create external pad links and finally register subdev nodes plus the media device. Streaming is driven from video nodes through pipeline enable/disable walking upstream. IRQs dispatch per-block handlers and mark pipeline errors on SBL overflow. Remove unregisters notifier/entities, cleans modules/xclks, detaches IOMMU under a temporary hardware reference, and frees media enums.

State and persistence: `struct isp_device` stores V4L2/media devices, notifier, MMIO bases, revision, syscon, phy type, IOMMU mapping, locks, stop/crash state, context-saved flag, refcount, clocks, xclks, all submodule structs, SBL resource bits, and subclock resource bits. Register context is saved in `isp_reg_list` plus OMAP IOMMU context on last put or PM prepare. No disk persistence exists.

Dependencies/integration: Depends on Linux platform/OF/fwnode graph, V4L2 async/media controller/subdev APIs, common clock framework, regulators, syscon regmap, OMAP IOMMU/ARM DMA-IOMMU, IRQs, and all internal OMAP3 ISP modules. It integrates with external camera sensors through OF endpoints and async notifier binding.

Risks and test signals: Pipeline stop failure marks entities crashed and can trigger ISP reset; preview crashes are specifically blocked from restart. Busy-wait stop loops lack sleep in `isp_pipeline_wait()` and need hardware timing validation. PM depends on prepare/suspend ordering because sensors may need ISP-provided clocks. Endpoint parsing assumes port IDs for parallel/CSIPHY1/CSIPHY2 and falls through CSI2/CSI1/CCP2 parsing. Test probe on ISP revisions 2.0 and 15.0, IOMMU attach failures, missing regulators/clocks/syscon, async sensor binding, all internal media links, stream start/stop for single-shot and continuous pipelines, SBL overflow error propagation, xclk rate changes, runtime refcount nesting, system suspend/resume with active streams, and removal after partial probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isp.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isp.h

Purpose: Defines the OMAP3 ISP core data model, register access helpers, resource enums, exported core APIs, and the aggregate `struct isp_device` shared by all ISP submodules.

Important APIs/types: Enums define MMIO resource indexes, SBL resources, subclock resources, xclk IDs, and revision/PHY constants. `struct isp_res_mapping` maps hardware revision to block offsets and PHY type. `struct isp_reg` supports context save/restore lists. `struct isp_xclk` represents an ISP-provided external clock. `struct isp_device` aggregates media/V4L2/notifier state, device resources, MMIO bases, syscon, IOMMU mapping, locks, crash/stop flags, refcount, clocks, xclks, CCDC/preview/resizer/CSI/CCP2/stat submodules, and resource bitmasks. `struct isp_async_subdev` stores async notifier connection plus bus config. Inline register helpers wrap raw read/write/clear/set/clear-set operations. Public functions cover flush, histogram DMA synchronization, module/pipeline stream control, bridge config, get/put, SBL/subclock resources, and entity registration.

Control flow: Included by nearly every OMAP3 ISP module. Submodules use `to_isp_device()` to recover the core, register helpers to access their MMIO windows, and exported functions to manage shared clocks/SBL/pipeline operations.

State and persistence: Declares all shared runtime state but stores none itself. Context persistence is volatile hardware-context save/restore managed by `isp.c`.

Dependencies/integration: Pulls in media entity, V4L2 async/device, clk provider, platform/device/wait headers, public `omap3isp.h`, and all internal submodule headers. This creates a central include hub for the driver.

Risks and test signals: Header coupling is high; changing `struct isp_device` or enum order can break every submodule and resource map. Raw MMIO helpers do not add barriers beyond raw access semantics, so callers must flush where required. Test full driver build after any signature/resource changes and exercise modules that use each MMIO range and subclock/SBL bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/isp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccdc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccdc.c

Purpose: Implements the OMAP3 ISP CCDC subdevice, the raw/YUV sensor front-end that receives parallel/CSI/CCP2 input, crops and formats it, writes frames to memory, feeds preview/resizer/statistics paths, manages lens shading compensation and faulty pixel correction tables, and handles CCDC-specific streaming/interrupt/pad operations.

Important APIs/functions: `omap3isp_ccdc_busy()`, `omap3isp_ccdc_isr()`, `omap3isp_ccdc_restore_context()`, `omap3isp_ccdc_max_rate()`, register/entity init/cleanup functions, and the V4L2 subdev ops form the external module API. LSC functions validate user config/table size, allocate coherent tables, program LSC registers, handle prefetch timeouts/errors, defer reconfiguration to VD1/LSC_DONE, and free old requests through workqueue. `ccdc_config()` implements private `VIDIOC_OMAP3ISP_CCDC_CFG` for ALAW, LPF, clamp, black compensation, FPC, and LSC. `ccdc_configure()` programs bridge, sync interface, Bayer color pattern, VD interrupts, crop geometry, memory line offsets, field handling, byte swap/pack, video port, LSC, and pending controls. `ccdc_set_stream()` controls subclock/SBL resources and starts/stops hardware for continuous, single-shot, or stopped states. Pad ops implement media-bus code enumeration, frame-size bounds, format propagation, crop selection, and link validation.

Control flow: Initialization sets locks/wait/workqueue defaults, applies initial clamp control, initializes the subdev/media entity/video node, and defaults formats. Link setup records one active input and one output role, rejecting unsupported multi-output pipeline combinations. On stream start from stopped, the CCDC subclock is enabled, registers are configured, and hardware starts immediately unless output-to-memory waits for a queued buffer. `ccdc_video_queue()` writes the buffer DMA address and restarts or marks underrun. IRQ dispatch handles VD1, LSC, VD0, and HS/VS: VD1 stops/reconfigures LSC or CCDC at frame boundary, VD0 completes memory buffers and applies deferred controls, HS/VS sends frame-sync events. Stream stop drives a CCDC/LSC stopping state machine and waits up to 2 seconds.

State and persistence: `struct isp_ccdc_device` holds active pad formats, crop, input/output bitmasks, output video node, control state, clamp/FPC/LSC table state, pending update bitmasks, BT.656 flag, field accumulation, underrun flag, stream state, locks, wait queue, stopping state, and running flag. DMA-coherent FPC and LSC tables persist until replaced, stream stop, cleanup, or workqueue free. No disk persistence.

Dependencies/integration: Depends on ISP core register/SBL/subclock/pipeline helpers, `ispvideo` buffer queues, media controller subdev framework, V4L2 events and private OMAP3 ISP userspace ABI structs, DMA coherent memory, usercopy, and hardware register definitions. It feeds preview/resizer/stat modules and can write to a capture video node.

Risks and test signals: LSC request locking is subtle because userspace ioctl, VD1/LSC_DONE IRQs, stream stop, and workqueue freeing share request/active/free queues. `ccdc_config()` uses `shadow_update` to avoid applying partial control updates in VD0, so usercopy failure paths need coverage. The stop state machine differs for BT.656 and external sync; timeout marks hardware risk. Format propagation sets video-port code to 0 for unsupported YUV, so enumeration/link paths must handle that. Test private ioctls for each control/table, LSC invalid size/offset/prefetch error, FPC replacement and cleanup, Bayer/YUV/BT.656 formats, interlaced/alternate field capture, buffer underrun/restart, single-shot restart, streamoff timeout recovery, media link exclusivity, frame-sync events, and context restore after suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccdc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccdc.h

Purpose: Declares the CCDC submodule interface and state structures for the OMAP3 ISP driver.

Important APIs/types: `enum ccdc_input_entity` identifies none, parallel, CSI2A, CCP2B, and CSI2C inputs. Output bitmasks select memory, preview, or resizer. LSC structs model state (`STOPPED`, `STOPPING`, `RUNNING`, `RECONFIG`), requested configs, coherent table storage, active/request/free queues, and deferred freeing work. Stop/event macros encode the CCDC/LSC stopping state machine. Pad constants define sink, output formatter source, and video-port source pads. `struct isp_ccdc_device` contains the V4L2 subdev, pads, formats, crop, input/output routing, video node, image controls, LSC/FPC resources, update flags, BT.656/field/underrun/streaming state, locks, wait queue, and ioctl mutex. Prototypes expose init/cleanup, entity registration, busy/ISR, context restore, and max-rate calculation.

Control flow: `isp.c` includes this header to embed `struct isp_ccdc_device`, initialize/register the module, dispatch interrupts, restore context, and ask rate limits. Other modules use pad/output constants when creating media links.

State and persistence: Declares in-memory state only. Coherent DMA table lifetime is managed by `ispccdc.c`.

Dependencies/integration: Includes public OMAP3 ISP ABI (`linux/omap3isp.h`), workqueues, and `ispvideo.h`. It forward-declares `struct isp_device` to avoid a full core dependency for function prototypes.

Risks and test signals: Stop/event bit encodings are consumed by interrupt code and wait conditions; changes require careful state-machine tests. The struct is central to both IRQ and userspace ioctl paths, so field ordering is internal but semantic grouping matters. Build and stream tests should cover all declared inputs/outputs and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccdc.h -->
