# Group Research: subset-b-004157

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-subdev.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-subdev.c

Purpose: implements the RZ/V2H(P) IVC V4L2 subdevice that sits between the video-output node and downstream raw-processing hardware. It exposes a two-pad pixel formatter media entity, maps 8/10/12/14/16/20-bit Bayer sink formats to fixed 20-bit Bayer source formats, and registers the associated video device once the subdevice is registered.

Important APIs and functions: `rzv2h_ivc_enum_mbus_code()`, `rzv2h_ivc_enum_frame_size()`, `rzv2h_ivc_set_fmt()`, `rzv2h_ivc_init_state()`, `rzv2h_ivc_registered()`, `rzv2h_ivc_link_validate()`, `rzv2h_ivc_initialise_subdevice()`, and `rzv2h_ivc_deinit_subdevice()`. The file defines `rzv2h_ivc_pad_ops`, `rzv2h_ivc_subdev_ops`, internal ops, and `media_entity_operations`.

Control flow: format enumeration distinguishes source and sink pads. Sink pad format changes are clamped to IVC min/max dimensions, default to a supported Bayer code when needed, then propagate to the source pad with the matching 20-bit output code. Stream enable/disable intentionally do nothing because power and register programming are driven by the video node's streamon path. Registration finalizes the subdev, async-registers it, and later creates the video device through the internal `registered` callback.

State and persistence: persistent state is held in the V4L2 subdev active state and in `ivc->format` for the video node. Link validation compares active subdev dimensions and media-bus code against the selected video pixel format. Cleanup removes links, unregisters the subdev, frees subdev state, and cleans the media entity.

Dependencies and integration: depends on `rzv2h-ivc.h`, V4L2 subdev/event/control helpers, media entity pads, and async subdev registration. It integrates with `rzv2h-ivc-video.c` through `rzv2h_ivc_init_vdev()` and validates media links created from the video output node to the IVC subdevice.

Risks and test signals: risk centers on code mapping mismatches between video fourcc formats and subdev Bayer codes, invalid width/height propagation, and cleanup order. Test with `media-ctl -p`, format enumeration on both pads, `VIDIOC_S_FMT` plus `media-ctl --set-v4l2`, link validation failures for incompatible Bayer order, and streamon/streamoff through the video node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-subdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-video.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-video.c

Purpose: implements the RZ/V2H(P) IVC V4L2 video-output node and vb2 queue. It accepts raw Bayer/CRU-packed frames from userspace or DMABUF, programs AXIRX and frame-manager registers, and feeds buffers into the IVC hardware for transfer to the subdevice pipeline.

Important APIs and functions: exported local driver entry points are `rzv2h_ivc_init_vdev()`, `rzv2h_deinit_video_dev_and_queue()`, `rzv2h_ivc_transfer_buffer()`, and `rzv2h_ivc_buffer_done()`. Key vb2 operations are `rzv2h_ivc_queue_setup()`, `rzv2h_ivc_buf_queue()`, `rzv2h_ivc_start_streaming()`, and `rzv2h_ivc_stop_streaming()`. IOCTL handlers enumerate and set `V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE` formats.

Control flow: queued vb2 buffers enter `ivc->buffers.queue` under `buffers.lock`. When streaming and no frame-valid interface state blocks progress, `rzv2h_ivc_transfer_buffer()` picks the next buffer, writes its DMA address to `AXIRX_SADDL_P0`, sets `vvalid_ifp`, and triggers `FM_FRCON`. The IRQ path in the device file calls `rzv2h_ivc_buffer_done()` and may transfer the next buffer. Streaming starts by resuming runtime PM, starting the media pipeline, configuring format registers, and priming a buffer; stop requests hardware frame stop, returns all buffers with error, stops the media pipeline, and autosuspends.

State and persistence: stores current `v4l2_pix_format_mplane`, selected `rzv2h_ivc_format`, sequence counter, current buffer, pending queue, and `vvalid_ifp` interrupt counter. Format configuration persists in hardware registers until stream stop or reconfiguration. Queue setup enforces one plane and a minimum `sizeimage`.

Dependencies and integration: uses vb2 dma-contig, runtime PM, V4L2 file/ioctl helpers, media pipeline helpers, MIPI CSI-2 datatype constants, and register helpers from `rzv2h-ivc-dev.c`. The video entity is linked immutably to the subdevice sink pad.

Risks and test signals: watch for races between `buffers.lock` and `spinlock`, polling timeout in stop, improper `try_fmt` use of `fmt.pix` versus `fmt.pix_mp`, and buffer leaks on start failures. Test with `v4l2-compliance`, multi-format `VIDIOC_TRY_FMT/S_FMT`, streaming with MMAP and DMABUF, link mismatch failures, runtime PM tracing, and IRQ-driven buffer completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc-video.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc.h

Purpose: shared private header for the RZ/V2H(P) Input Video Control driver. It centralizes register offsets, bit fields, image limits, format descriptors, pad numbering, the top-level device state, and cross-file function prototypes.

Important APIs and types: defines AXIRX and frame-manager register offsets such as `RZV2H_IVC_REG_AXIRX_PXFMT`, `RZV2H_IVC_REG_AXIRX_SADDL_P0`, `RZV2H_IVC_REG_FM_STOP`, and interrupt bits. `struct rzv2h_ivc_format` ties video fourcc, acceptable media-bus codes, and MIPI datatype. `struct rzv2h_ivc` stores device resources, video device, subdevice, buffer queue state, active format, mutex, and spinlocks.

Control flow role: the header is not executable, but it defines the contract among the platform device, subdevice, and video-node files. Device probe allocates/populates `struct rzv2h_ivc`; subdev setup uses the pad enum and format limits; video streaming uses the register definitions and buffer fields; IRQ handling updates `vvalid_ifp`, completes buffers, and calls transfer helpers.

State and persistence: persistent driver state includes MMIO base, clock/reset arrays sized by `RZV2H_IVC_NUM_HW_RESOURCES`, IRQ number, current V4L2 format, current and queued buffers, and stream sequence. The header's locks document ownership: `buffers.lock` guards queue/current buffer and `spinlock` protects interrupt-facing state.

Dependencies and integration: includes Linux clock/reset/list/mutex/spinlock/workqueue types plus V4L2, media entity, subdev, and vb2 headers. Prototypes connect `rzv2h-ivc-dev.c`, `rzv2h-ivc-subdev.c`, and `rzv2h-ivc-video.c`.

Risks and test signals: changes here have broad ABI-like impact inside the driver. Validate register bit definitions against hardware documentation, ensure new formats keep fourcc/mbus/datatype mappings coherent, and run compile tests for all three translation units after structural changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzv2h-ivc/rzv2h-ivc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/sh_vou.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/sh_vou.c

Purpose: legacy SuperH Video Output Unit platform driver. It exposes a V4L2 video-output device for analog output, manages a vb2 dma-contig queue, configures SuperH VOU registers, and drives an external I2C encoder subdevice using platform data.

Important APIs and functions: register helpers `sh_vou_reg_*`, vb2 ops `sh_vou_queue_setup()`, `sh_vou_buf_prepare()`, `sh_vou_buf_queue()`, `sh_vou_start_streaming()`, `sh_vou_stop_streaming()`, format/selection/std handlers, `sh_vou_isr()`, `sh_vou_hw_init()`, `sh_vou_open()`, `sh_vou_release()`, `sh_vou_probe()`, and `sh_vou_remove()`. Main state is `struct sh_vou_device`.

Control flow: probe validates platform data, maps MMIO, requests IRQ, registers a V4L2 device, initializes a vb2 output queue, binds an I2C encoder subdev, initializes hardware, then registers the video node. Open performs first-use runtime PM resume and hardware init. Streaming requires two queued buffers, programs mirror address banks for the first two frames, enables VSYNC interrupts, and turns the VOU on. The ISR acknowledges frame events, completes the active buffer, advances sequence/timestamp, and schedules the next queued buffer or reuses the current buffer when underrun would occur.

State and persistence: stores current pixel format, compose rectangle, standard, active buffer, queued list, status enum, and sequence. Register state persists across active use and is reset/reinitialized on first open. Geometry helpers choose supported scaling ratios and coordinate output crop/composition with the external encoder's pad format and selection.

Dependencies and integration: uses platform data from `media/drv-intf/sh_vou.h`, V4L2 common/device/ioctl/media-bus APIs, vb2 dma-contig, runtime PM, I2C subdev creation, and platform IRQ/MMIO resources.

Risks and test signals: risks include legacy platform-data assumptions, two-buffer minimum behavior, static variables in ISR diagnostics, hardcoded encoder bus code, incomplete PAL support, and close/open runtime PM ordering. Test with `v4l2-compliance`, write/MMAP/DMABUF output, NTSC/PAL standard switching where supported, compose selection changes, IRQ buffer churn, and encoder subdevice failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/sh_vou.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/Makefile

Purpose: builds the Renesas VSP1/VSP2 driver as a single composite kernel object `vsp1.o` when `CONFIG_VIDEO_RENESAS_VSP1` is enabled. It declares the full object list for core, V4L2 media-controller, DRM/DU, display-list, video-node, read/write pixel formatter, and processing entities.

Important APIs and functions: no C APIs are defined here. The key build contract is `vsp1-y := ...` plus `obj-$(CONFIG_VIDEO_RENESAS_VSP1) += vsp1.o`. Included object files are `vsp1_drv.o`, `vsp1_entity.o`, `vsp1_pipe.o`, `vsp1_dl.o`, `vsp1_drm.o`, `vsp1_video.o`, RPF/WPF/RWPF support, CLU/HSIT/LUT/BRX/SRU/UDS/HGO/HGT/HISTO, IIF/LIF/UIF, and VSPX support.

Control flow role: link order makes all subsystem objects part of one module or built-in driver. `vsp1_drv.o` provides platform probe/remove and module registration, while the other objects provide helpers and entity constructors called from probe-time entity creation or runtime pipeline configuration.

State and persistence: no runtime state. Its persistence concern is build composition: omitting an object silently breaks constructor references or feature support for hardware variants declared in `vsp1_drv.c`.

Dependencies and integration: integrates with Kbuild and the Renesas media-platform Kconfig entry. It assumes all listed sources compile under the same configuration and share private headers in this directory.

Risks and test signals: risks are stale object lists when adding/removing entity files, missing feature support for new hardware blocks, and unresolved symbols from conditional edits. Test with `make drivers/media/platform/renesas/vsp1/` or a kernel `allyesconfig`/target defconfig build with `CONFIG_VIDEO_RENESAS_VSP1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1.h

Purpose: primary private header for the VSP1 driver. It defines hardware feature flags, per-SoC device metadata, global device state, maximum entity counts, register access wrappers, and core lifecycle prototypes.

Important APIs and types: `struct vsp1_device_info` describes model/version/generation/features/counts/uapi mode. `struct vsp1_device` owns MMIO, FCP/bus-master/reset resources, all entity pointers, media/V4L2 devices, entity/video lists, and DRM/VSPX private pointers. `vsp1_feature()`, `vsp1_read()`, `vsp1_write()`, `vsp1_device_get()`, `vsp1_device_put()`, and `vsp1_reset_wpf()` are the main cross-file helpers.

Control flow role: probe fills `struct vsp1_device`, looks up `info`, then entity constructors populate the typed pointers. Runtime paths acquire the device through runtime PM, write registers directly or through display lists, and use feature flags to select entity availability, extended display-list support, LIF quirks, flips, and VSPX/IIF paths.

State and persistence: persistent state includes hardware resources, active media graph objects, and pointers used by both UAPI and DRM modes. Feature flags persist as immutable capabilities after probe. Register access functions are thin MMIO wrappers with no locking, so callers own ordering and power state.

Dependencies and integration: includes Linux IO/list/mutex, media-device, V4L2 device/subdev, and `vsp1_regs.h`. It forward-declares all major internal entity types and integrates with R-Car FCP and reset controller support.

Risks and test signals: edits can affect almost every VSP1 object. Validate feature-bit additions against entity creation, route setup, Kbuild, and runtime PM. Compile-test all VSP1 objects, then test both media-controller UAPI devices and DRM display integration on variants with different `vsp1_device_info` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_brx.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_brx.c

Purpose: implements the VSP1 blend/ROP entities, covering both BRU and BRS variants. It exposes V4L2 subdev pad operations, a background-color control, and stream-time register programming for composition and alpha blending.

Important APIs and functions: `vsp1_brx_create()`, `brx_set_format()`, `brx_get_selection()`, `brx_set_selection()`, `brx_configure_stream()`, and the `brx_entity_ops` callback table. The file uses `struct vsp1_brx` from `vsp1_brx.h` and shared entity helpers.

Control flow: entity creation chooses BRU or BRS base registers and pad count, initializes the common entity, and installs `V4L2_CID_BG_COLOR`. Format setting forces all pads to ARGB8888 or AYUV, clamps dimensions, propagates sink-0 code to all pads, and resets compose rectangles. Selection controls per-input compose location with no scaling. During stream configuration, it writes input normalization, virtual background size/color, BRU ROP routing, per-input control, and blending coefficients to the display list body.

State and persistence: persistent state includes `bgcolor` and `inputs[i].rpf`, the latter set by DRM pipeline setup to mark active inputs. Pad formats and compose rectangles live in entity subdev state. Hardware state is persisted through display-list entries and refreshed whenever the pipeline is configured.

Dependencies and integration: depends on `vsp1_entity`, `vsp1_dl`, `vsp1_pipe`, `vsp1_rwpf`, and V4L2 controls. DRM code allocates and arbitrates BRU/BRS use; media-controller mode exposes links to userspace.

Risks and test signals: risks include mismatched pad format propagation, incorrect premultiplied-alpha handling, BRU/BRS input ordering, and background alpha assumptions. Test multi-plane DRM composition with z-order changes, UAPI media link setup through BRU/BRS, BG color control changes, and ARGB/AYUV format negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_brx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_brx.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_brx.h

Purpose: declares the VSP1 BRU/BRS blend entity state and constructor. It is the shared contract between entity creation, DRM pipeline setup, and BRx stream configuration.

Important APIs and types: `BRX_PAD_SINK(n)` maps input pad indexes. `struct vsp1_brx` embeds `struct vsp1_entity`, the register `base`, a V4L2 control handler, `inputs[VSP1_MAX_RPF]` linking BRx pads to active RPFs, and `bgcolor`. `to_brx()` converts from subdev to container, and `vsp1_brx_create()` constructs either `VSP1_ENTITY_BRU` or `VSP1_ENTITY_BRS`.

Control flow role: `vsp1_drv.c` calls `vsp1_brx_create()` based on feature flags. `vsp1_drm.c` uses `to_brx()` and `inputs[]` to sort and attach RPF layers. `vsp1_brx.c` uses the same structure for V4L2 controls and display-list register generation.

State and persistence: `inputs[]` is transient pipeline state but persists across atomic DRM setup until reconfigured. `bgcolor` persists as a V4L2 control-backed value. The embedded entity owns pad state, routing, pipe membership, and media links.

Dependencies and integration: includes media entity, V4L2 controls/subdev, and `vsp1_entity.h`; forward-declares `vsp1_device` and `vsp1_rwpf`.

Risks and test signals: array sizing must remain compatible with maximum RPF and BRU pad counts. Test compile with variants that expose BRU only, BRS only, and both, and exercise DRM layer count transitions above and below two inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_brx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_clu.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_clu.c

Purpose: implements the VSP1 cubic look-up table processor. It exposes a V4L2 subdevice with 2D/3D mode control and a 17x17x17 U32 LUT control, then injects LUT table programming into display lists.

Important APIs and functions: `vsp1_clu_create()`, `clu_set_table()`, `clu_s_ctrl()`, `clu_configure_stream()`, `clu_configure_frame()`, and `clu_destroy()`. Supported media bus formats are ARGB, AHSV, and AYUV 32-bit packed formats.

Control flow: userspace writes LUT and mode controls. Table updates allocate a display-list body from a small pool, write `VI6_CLU_ADDR` and all `VI6_CLU_DATA` entries, then swap it into `clu->clu` under a spinlock. Stream configuration caches whether the stream is AYUV. Per-frame configuration enables CLU, optionally sets 2D mode when requested and YUV, then consumes the pending LUT body by adding it to the current display list and dropping the local reference.

State and persistence: persistent control state includes `mode`, `yuv_mode`, pending `clu` display-list body, and the body pool. The table is not written directly to MMIO; it persists as queued DMA display-list entries until consumed by hardware. Spinlock protects table-body handoff between control updates and frame configuration.

Dependencies and integration: depends on V4L2 custom controls, common entity pad helpers, `vsp1_dl_body_pool_create()`, and display-list body ownership rules.

Risks and test signals: risks include pool exhaustion on rapid table updates, lost updates due to swap semantics, 2D mode only being valid for YUV, and large control payload validation. Test by setting CLU table while streaming, checking memory leak/refcount behavior, toggling 2D/3D modes, and validating visual output or register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_clu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_clu.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_clu.h

Purpose: declares private state for the VSP1 cubic LUT entity.

Important APIs and types: defines `CLU_PAD_SINK`, `CLU_PAD_SOURCE`, `struct vsp1_clu`, `to_clu()`, and `vsp1_clu_create()`. `struct vsp1_clu` embeds the common entity, V4L2 control handler, `yuv_mode`, spinlock, selected mode, pending table display-list body pointer, and display-list body pool.

Control flow role: the header lets `vsp1_drv.c` create a CLU entity and lets `vsp1_clu.c` convert subdev callbacks back to CLU-specific state. The pad macros align with the two-pad common entity format operations.

State and persistence: `yuv_mode` is cached from stream format and used by frame configuration. `mode` is control-backed. `clu` points to a pending DMA display-list body containing table writes; `pool` owns reusable bodies sized for CLU table uploads.

Dependencies and integration: includes spinlock, media entity, V4L2 controls/subdev, and `vsp1_entity.h`; forward-declares `vsp1_device` and `vsp1_dl_body`.

Risks and test signals: any structural change must preserve locking between control updates and frame configuration. Compile-test CLU-enabled variants and run control set/get plus stream tests that update the LUT during active pipelines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_clu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_dl.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_dl.c

Purpose: implements VSP1 display-list allocation, register-write body pools, optional extended commands, list commit, and frame-end lifecycle management. It is the main persistence layer for hardware register programming across both mem-to-mem and DRM pipelines.

Important APIs and functions: body APIs `vsp1_dl_body_pool_create()`, `vsp1_dl_body_get()`, `vsp1_dl_body_put()`, `vsp1_dl_body_write()`; list APIs `vsp1_dl_list_get()`, `vsp1_dl_list_get_body0()`, `vsp1_dl_list_add_body()`, `vsp1_dl_list_add_chain()`, `vsp1_dl_list_commit()`, `vsp1_dl_list_put()`; manager APIs `vsp1_dlm_create()`, `vsp1_dlm_setup()`, `vsp1_dlm_irq_frame_end()`, `vsp1_dlm_reset()`, and `vsp1_dlm_destroy()`.

Control flow: `vsp1_dlm_create()` allocates a manager, DMA body pool, preallocated lists, and extended command pool when supported. Entity configuration writes register entries into list bodies. Commit fills headers for the head and chained lists, then either enqueues directly in single-shot mode or manages queued/pending replacement in continuous mode. The IRQ frame-end handler retires active lists, promotes queued lists, sends pending updates to hardware, and returns completion/writeback/internal flags.

State and persistence: DMA write-combined pools hold display-list bodies and headers. Lists move through free, active, queued, and pending states under `dlm->lock`. Bodies use refcounts because LUT/CLU table bodies can be shared with a list while the caller drops its local reference. Extended pre-command state is pooled and reset on release.

Dependencies and integration: depends on DMA mapping, spinlocks, refcounting, VSP1 register definitions, and bus-master selection from `vsp1_device`. All entity `configure_*` callbacks and pipeline runners rely on this file.

Risks and test signals: risks include header byte-count mistakes, races with hardware `UPDHDR`, pending-list replacement while waiters expect internal completion, body pool exhaustion, and chain release recursion. Test with streaming mem-to-mem, continuous DRM atomic updates, writeback completion, LUT/CLU rapid updates, partitioned pipelines, and lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_dl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_dl.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_dl.h

Purpose: public-private interface for VSP1 display-list management used by all VSP1 entities, pipelines, video paths, and DRM integration.

Important APIs and types: declares opaque `vsp1_dl_body`, `vsp1_dl_body_pool`, `vsp1_dl_list`, and `vsp1_dl_manager`; frame-end flags `VSP1_DL_FRAME_END_COMPLETED`, `VSP1_DL_FRAME_END_WRITEBACK`, and `VSP1_DL_FRAME_END_INTERNAL`; and `struct vsp1_dl_ext_cmd` for extended display-list command payloads. Function prototypes cover manager setup/create/reset/destroy, body pool lifecycle, body writes, list acquisition, chaining, and commit.

Control flow role: callers acquire a list from a manager, obtain body0, write register/data pairs through `vsp1_dl_body_write()`, optionally attach extra bodies or chains, and commit with frame-end flags. IRQ code calls `vsp1_dlm_irq_frame_end()` to retire or promote list state.

State and persistence: the header abstracts DMA-backed persistent list state while hiding implementation details. The frame-end flags intentionally mirror external DU status bits, making this header part of the DRM notification contract.

Dependencies and integration: includes Linux types and uses `list_head`, DMA addresses, and VSP1 device types indirectly. It is included by almost every entity implementation.

Risks and test signals: changing flag values can break DU status synchronization. Prototype changes affect many objects. Compile all VSP1 sources and run streaming tests that cover single-shot, continuous, chained, extended-DL, and writeback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_dl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drm.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drm.c

Purpose: implements the in-kernel VSP1 interface used by the Renesas DU DRM/KMS driver. It configures internal display pipelines, maps DRM plane state onto RPF/BRx/WPF/LIF entities, handles CRC/writeback, and exports DU-facing symbols.

Important APIs and functions: exported functions include `vsp1_du_init()`, `vsp1_du_setup_lif()`, `vsp1_du_atomic_begin()`, `vsp1_du_atomic_update()`, `vsp1_du_atomic_flush()`, `vsp1_du_map_sg()`, and `vsp1_du_unmap_sg()`. Internal helpers set up RPF inputs, arbitrate BRU/BRS, insert UIF for CRC, set output formats, configure entities, and signal DU completion.

Control flow: `vsp1_drm_init()` creates one pipeline per LIF and permanently attaches WPF and LIF. `vsp1_du_setup_lif()` enables or disables a CRTC pipeline; enable sets dimensions, configures input/output formats, resumes the device, commits an initial display list, and starts the pipeline. Atomic update stores per-RPF memory, format, crop, compose, zpos, alpha, and color range. Atomic flush optionally configures writeback, re-sorts inputs by z-order, reconfigures BRx/UIF/RPF links, and commits a new display list.

State and persistence: `struct vsp1_drm` stores pipeline state, global lock, and per-RPF input rectangles/color metadata. `force_brx_release` plus wait queues coordinate sharing BRU/BRS between two display pipelines. Display-list managers persist active hardware configuration until replaced at frame end.

Dependencies and integration: depends on `include/media/vsp1.h` DU API, V4L2 subdev pad operations, DMA mapping through the VSP/FCP bus master, VSP1 entity/display-list/pipeline helpers, and UIF CRC support.

Risks and test signals: risks include BRx arbitration timeouts, stale disabled RPFs remaining in hardware routes, format propagation failures, writeback flag lifetime, and non-coherent DMA assumptions. Test atomic modesets, plane enable/disable/z-order changes, dual-pipeline BRU/BRS contention, CRC source selection, writeback capture, and suspend/resume with active display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drm.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drm.h

Purpose: declares the private DRM/DU integration state for VSP1 display pipelines.

Important APIs and types: `struct vsp1_drm_pipeline` wraps a generic `vsp1_pipeline`, one cached partition, output width/height, BRx release coordination, optional UIF entity, CRC configuration, and DU completion callback/private data. `struct vsp1_drm` contains per-LIF pipelines, a mutex protecting BRU/BRS allocation, and per-RPF input crop/compose/zpos/color state. `to_vsp1_drm_pipeline()` converts from generic pipeline to DRM wrapper. `vsp1_drm_init()` and `vsp1_drm_cleanup()` are local lifecycle APIs.

Control flow role: `vsp1_drv.c` calls init/cleanup for non-UAPI display-oriented VSP instances. `vsp1_drm.c` fills and consumes the structures during DU setup and atomic updates.

State and persistence: this header defines the persistent state that survives across DRM atomic commits: selected output geometry, current input rectangles, z-order, color metadata, callback, CRC source, and BRx ownership flags.

Dependencies and integration: includes Linux mutex/wait/V4L2 types, the external media VSP1 API for DU config structures, and `vsp1_pipe.h`.

Risks and test signals: structure changes can break assumptions in both pipeline configuration and frame-end callbacks. Test dual-LIF devices, CRC toggling, writeback, disabled-input transitions, and concurrent atomic commits serialized by the DRM lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drv.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drv.c

Purpose: platform driver core for Renesas VSP1/VSP2. It probes resources, identifies hardware variants, creates entities and media links, handles IRQs and runtime PM, and registers either a V4L2 userspace media graph or an internal DRM/VSPX pipeline.

Important APIs and functions: `vsp1_irq_handler()`, `vsp1_create_entities()`, `vsp1_destroy_entities()`, `vsp1_device_init()`, `vsp1_reset_wpf()`, `vsp1_device_get()`, `vsp1_device_put()`, PM callbacks, `vsp1_lookup_info()`, `vsp1_probe()`, and `vsp1_remove()`. The large `vsp1_device_infos[]` table maps IP versions to features and entity counts.

Control flow: probe allocates `vsp1_device`, maps MMIO, gets IRQ/reset/FCP, enables runtime PM, reads or synthesizes the version, masks stale interrupts, requests IRQ, and creates entities. Entity creation instantiates feature-gated processors, RPF/WPF/video nodes, registers subdevs, then either creates userspace media links and subdev nodes or initializes DRM/VSPX support. IRQ handling scans WPFs, acknowledges DFE/FRE/UND bits, counts underruns, and dispatches frame-end handling.

State and persistence: persistent state is rooted in `struct vsp1_device`, entity/video lists, hardware feature table, runtime PM state, reset/FCP resources, media/V4L2 devices, and optional DRM/VSPX private state. Runtime resume resets routes to unused, resets active WPFs, configures display-list engine, and enables FCP.

Dependencies and integration: depends on platform device, OF match data, reset controller, runtime PM, R-Car FCP, V4L2/media core, and every VSP1 entity constructor.

Risks and test signals: risks include incomplete cleanup after partial entity creation, unsupported version detection, interrupt acknowledgment polarity, runtime PM reset side effects, and feature-count mismatches. Test probe/remove deferral, suspend/resume, all compatible strings, UAPI media graph enumeration, DRM display operation, and WPF underrun logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_entity.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_entity.c

Purpose: common VSP1 entity infrastructure. It owns media-subdev initialization, default pad format operations, media link bookkeeping, route register setup, entity state allocation, and wrapper dispatch for entity-specific stream/frame/partition callbacks.

Important APIs and functions: `vsp1_entity_init()`, `vsp1_entity_destroy()`, `vsp1_entity_route_setup()`, `vsp1_entity_configure_stream()`, `vsp1_entity_configure_frame()`, `vsp1_entity_configure_partition()`, `vsp1_entity_adjust_color_space()`, `vsp1_entity_link_setup()`, `vsp1_entity_remote_pad()`, and generic pad handlers for format/code/frame-size. `vsp1_routes[]` maps entity type/index to DPR route registers and node IDs.

Control flow: constructors initialize a `vsp1_entity`, allocate pads/sources, bind route entries, initialize subdev ops/state, and attach media entity operations. During media link setup, source fan-out and sink fan-in are enforced in software while ignoring histogram side links for normal pipeline traversal. During hardware configuration, route setup writes the correct DPR routing value, with special handling for HGO/HGT sampling and BRS/IIF selector bits.

State and persistence: `entity->state` stores active pad formats, crops, and compose rectangles. `sources[]`, `sink`, `sink_pad`, `pipe`, and list nodes persist the current graph/pipeline membership. The mutex protects subdev state; route entries are immutable after init.

Dependencies and integration: depends on V4L2 subdev state, media links, V4L2 controls/events, display-list writes, pipeline helpers, and format/color-space helpers from `vsp1_pipe.c`.

Risks and test signals: risks include use of internal `__v4l2_subdev_state_alloc()`, link bookkeeping divergence from media graph flags, route table gaps for new entities, and lock ordering. Test media link enable/disable, invalid fan-in/fan-out, format propagation, route register traces, and all entity constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_entity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_entity.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_entity.h

Purpose: defines the common VSP1 entity abstraction used by all processing blocks. It provides entity type IDs, routing descriptors, operation callbacks, embedded state fields, and shared helper prototypes.

Important APIs and types: `enum vsp1_entity_type`, `struct vsp1_route`, `struct vsp1_entity_operations`, and `struct vsp1_entity`. The operation table separates stream-invariant setup, per-frame setup, per-partition setup, width limits, and partition construction. Helpers include `to_vsp1_entity()`, `vsp1_entity_init()`, `vsp1_entity_destroy()`, link setup, state lookup, route setup, configure dispatch, color-space adjustment, remote-pad lookup, and generic subdev pad handlers.

Control flow role: every entity constructor fills type, codes, limits, ops, and then calls `vsp1_entity_init()`. Pipeline configuration walks entities and dispatches the callbacks declared here. Media-controller mode relies on the link setup and pad handlers to build legal graphs.

State and persistence: `struct vsp1_entity` persists hardware identity, route pointer, supported bus codes, dimensions, pipeline membership, media pads, source/sink relationships, subdev active state, and a mutex protecting that state.

Dependencies and integration: includes Linux list/mutex and V4L2 subdev APIs; forward-declares VSP1 display-list and pipeline structures to avoid circular includes.

Risks and test signals: changing fields or callback semantics affects all entities. Validate compile coverage, media graph creation, route setup, pipeline partitioning, and subdev state locking after edits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_entity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgo.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgo.c

Purpose: implements the VSP1 1D histogram generator entity and metadata readout path. It configures HGO sampling/crop/downscale parameters and reads histogram registers into queued metadata buffers at frame end.

Important APIs and functions: `vsp1_hgo_create()`, `vsp1_hgo_frame_end()`, `hgo_configure_stream()`, plus controls for maximum RGB mode and number of bins. It reuses `vsp1_histogram_init()` for the subdev and metadata capture node.

Control flow: frame-end handling obtains a queued histogram buffer, reads max/min and sum registers, then reads either 256 green bins, 64 green bins, or separate 64-bin RGB histograms depending on controls. Stream configuration resets HGO registers, writes offset and size from crop selection, snapshots controls under the handler lock, computes horizontal/vertical ratio from crop and compose rectangles, and writes `VI6_HGO_MODE`.

State and persistence: persistent state includes `max_rgb`, `num_bins`, V4L2 control pointers, and the embedded histogram queue/entity state. Readout uses IRQ queue state from `vsp1_histo.c`; hardware register configuration is persisted through display-list entries.

Dependencies and integration: depends on HGO registers, display-list writes, V4L2 controls, vmalloc metadata buffers, and shared histogram infrastructure. `vsp1_drv.c` only creates HGO in UAPI mode on variants with the feature flag.

Risks and test signals: risks include control/layout changes while streaming, buffer payload size differences by mode, gen-dependent 256-bin support, and register read latency in frame-end context. Test metadata capture with all modes, no-buffer frame ends, crop/compose ratio changes, and `v4l2-compliance` metadata queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgo.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgo.h

Purpose: declares the 1D histogram generator private structure and frame-end API.

Important APIs and types: `struct vsp1_hgo` embeds `struct vsp1_histogram`, a nested control handler with `max_rgb` and optional `num_bins` controls, plus cached `max_rgb` and `num_bins` values. `to_hgo()` converts from subdev. `vsp1_hgo_create()` constructs the entity and metadata node; `vsp1_hgo_frame_end()` reads data at frame completion.

Control flow role: pipeline/frame-end code calls `vsp1_hgo_frame_end()` for HGO entities, while probe-time entity creation uses `vsp1_hgo_create()`. Control state is cached by stream configuration before register programming.

State and persistence: cached control values determine output payload layout. Embedded histogram state owns vb2 queue, wait queue, IRQ queue, metadata format, and media entity state.

Dependencies and integration: includes V4L2 control/subdev and `vsp1_histo.h`, which supplies the shared metadata capture implementation.

Risks and test signals: ensure consumers understand payload size varies by mode. Test both 64-bin and 256-bin capable hardware, max-RGB mode, and metadata buffer sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgt.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgt.c

Purpose: implements the VSP1 2D hue histogram generator. It configures hue-area boundaries, crop/downscale parameters, and reads fixed-size hue histogram metadata at frame end.

Important APIs and functions: `vsp1_hgt_create()`, `vsp1_hgt_frame_end()`, `hgt_hue_areas_try_ctrl()`, `hgt_hue_areas_s_ctrl()`, and `hgt_configure_stream()`. The custom `V4L2_CID_VSP1_HGT_HUE_AREAS` U8 array control holds six lower/upper hue areas.

Control flow: control validation enforces hardware ordering constraints for the 12 hue boundaries, including wrap-around behavior for area 0. Stream configuration resets HGT, writes crop offset/size, snapshots hue boundaries under the control lock, writes each area register, computes downscale ratios from crop/compose, and writes mode. Frame-end readout obtains a metadata buffer, reads max/min and sum, then reads six by 32 histogram bins.

State and persistence: `hue_areas[]` persists control state and is used for register programming. Embedded histogram state persists metadata queue and subdev state. Hardware programming is represented in display-list entries and refreshed at stream configuration.

Dependencies and integration: depends on shared histogram infrastructure, display-list writes, V4L2 controls, and HGT register definitions. Created only for feature-enabled UAPI devices.

Risks and test signals: risks include invalid hue boundary acceptance, fixed payload-size assumptions, crop/compose divide behavior, and no queued metadata buffers. Test control boundary validation, frame-end metadata capture, AHSV-only format negotiation, and selection changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgt.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgt.h

Purpose: declares the 2D histogram generator private structure and public local functions.

Important APIs and types: defines `HGT_NUM_HUE_AREAS` as six, `struct vsp1_hgt` with embedded `vsp1_histogram`, V4L2 control handler, and 12-byte hue boundary cache. `to_hgt()`, `vsp1_hgt_create()`, and `vsp1_hgt_frame_end()` are the conversion, constructor, and frame-end readout APIs.

Control flow role: `vsp1_drv.c` creates HGT when supported, and pipeline frame-end code uses `vsp1_hgt_frame_end()` to complete metadata buffers. `vsp1_hgt.c` owns all control validation and register programming.

State and persistence: hue areas persist in `hue_areas[]`; queue/readout state persists in the embedded histogram object.

Dependencies and integration: includes media/V4L2 control/subdev headers and shared `vsp1_histo.h`.

Risks and test signals: if `HGT_NUM_HUE_AREAS` or structure layout changes, both control dimensions and register programming must change. Test hue-area controls and metadata output size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hgt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_histo.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_histo.c

Purpose: shared implementation for VSP1 histogram metadata entities. It combines a V4L2 subdevice for image-side statistics sampling with a V4L2 metadata capture video node and vb2-vmalloc queue for readout buffers.

Important APIs and functions: `vsp1_histogram_init()`, `vsp1_histogram_destroy()`, `vsp1_histogram_buffer_get()`, `vsp1_histogram_buffer_complete()`, vb2 queue ops, histogram pad format/selection handlers, and metadata V4L2 ioctl/file operations.

Control flow: entity-specific HGO/HGT constructors call `vsp1_histogram_init()` with entity type, name, formats, data size, and metadata fourcc. Users queue metadata buffers to `irqqueue`. On frame end, HGO/HGT code calls `vsp1_histogram_buffer_get()`, fills the buffer, then calls `vsp1_histogram_buffer_complete()` to timestamp, sequence, set payload, complete vb2, clear readout, and wake stop waiters. Stop streaming returns queued buffers with error and waits for an in-progress readout.

State and persistence: `struct vsp1_histogram` stores metadata format/size, video node, media pad, vb2 queue, IRQ queue, wait queue, and `readout` flag. Subdev state stores sink crop/compose and a metadata fixed source pad. Locks split normal queue access (`lock`) from IRQ queue/readout (`irqlock`).

Dependencies and integration: depends on V4L2 ioctl/subdev, vb2-vmalloc, media entities, and shared entity helpers. HGO/HGT supply hardware-specific frame-end readers and stream configuration.

Risks and test signals: risks include waiting under IRQ lock, buffer completion during stop, metadata source pad semantics, and crop/compose ratio rounding. Test metadata queue lifecycle, streamoff during readout, selection API, payload sizes, and no-buffer frame ends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_histo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_histo.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_histo.h

Purpose: declares shared histogram metadata capture structures used by HGO and HGT.

Important APIs and types: defines `HISTO_PAD_SINK`, `HISTO_PAD_SOURCE`, `struct vsp1_histogram_buffer`, and `struct vsp1_histogram`. Conversion helpers are `vdev_to_histo()` and `subdev_to_histo()`. APIs include `vsp1_histogram_init()`, `vsp1_histogram_destroy()`, `vsp1_histogram_buffer_get()`, and `vsp1_histogram_buffer_complete()`.

Control flow role: HGO/HGT create their entities through `vsp1_histogram_init()`, then frame-end readers use buffer get/complete helpers. The embedded video node exposes metadata capture while the embedded `vsp1_entity` participates in the media graph.

State and persistence: queue state includes vb2 queue, IRQ queue list, wait queue, and `readout` in-progress flag. `data_size` and `meta_format` persist the ABI presented by the metadata node.

Dependencies and integration: includes Linux list/mutex/spinlock, media entity/V4L2 device/vb2, and `vsp1_entity.h`.

Risks and test signals: header changes affect both histogram implementations. Test compilation of HGO/HGT, metadata capture node registration, and streamoff with queued/readout buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_histo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hsit.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hsit.c

Purpose: implements VSP1 hue/saturation/value transform entities: HST converts ARGB to AHSV and HSI converts AHSV back to ARGB. Both are represented by the same structure with an `inverse` flag.

Important APIs and functions: `vsp1_hsit_create()`, `hsit_enum_mbus_code()`, `hsit_enum_frame_size()`, `hsit_set_format()`, and `hsit_configure_stream()`. Supported codes are ARGB8888 and AHSV8888.

Control flow: constructor picks entity type/name based on `inverse`. Enumeration reports fixed sink/source codes according to direction. Format setting only accepts sink changes, clamps dimensions, propagates to source, and swaps the media-bus code for the conversion direction. Stream configuration writes either `VI6_HSI_CTRL_EN` or `VI6_HST_CTRL_EN` into the display list.

State and persistence: persistent entity state includes `inverse`, pad formats in active subdev state, route information from common entity initialization, and pipeline membership. There is no separate runtime control state.

Dependencies and integration: depends on V4L2 subdev APIs, display-list body writes, entity helpers, and route setup in `vsp1_entity.c`. `vsp1_drv.c` creates both HSI and HST when `VSP1_HAS_HSIT` is set.

Risks and test signals: risks include incorrect direction-specific code enumeration, color-space adjustment for ARGB/AHSV, and bitwise `|` used in boolean tests. Test format negotiation on both pads, ARGB-to-AHSV and AHSV-to-ARGB graph construction, stream register traces, and media link validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hsit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hsit.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hsit.h

Purpose: declares the shared HSI/HST transform entity wrapper.

Important APIs and types: defines `HSIT_PAD_SINK`, `HSIT_PAD_SOURCE`, `struct vsp1_hsit` with embedded common entity and `inverse` direction flag, `to_hsit()`, and `vsp1_hsit_create()`.

Control flow role: `vsp1_drv.c` creates one inverse HSI and one non-inverse HST entity. `vsp1_hsit.c` uses `inverse` to select media-bus code direction and control register.

State and persistence: `inverse` is immutable after construction. All mutable format and graph state is stored by the embedded `vsp1_entity`.

Dependencies and integration: includes media entity/V4L2 subdev and common entity declarations.

Risks and test signals: callers must pass the correct direction flag. Test both generated entity names/types and pad format behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_hsit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_iif.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_iif.c

Purpose: implements the VSPX ISP Interface entity. It is an internal, three-pad processor used by VSPX-style pipelines and supports grayscale/raw-style media bus codes plus metadata.

Important APIs and functions: `vsp1_iif_create()` and `iif_configure_stream()`. Pad operations reuse generic entity handlers for code/frame-size/format enumeration and setting.

Control flow: constructor initializes an IIF entity with min/max dimensions, supported codes, three pads, and a placeholder media entity function because the entity is not exposed directly to userspace. Stream configuration writes `VI6_IIF_CTRL_CTRL` into the display list to enable/configure the block.

State and persistence: mutable state is the embedded `vsp1_entity` active subdev state, routes, media links, and pipeline membership. There are no controls or per-frame private fields. Hardware state persists through display-list programming.

Dependencies and integration: depends on `vsp1.h`, `vsp1_dl.h`, `vsp1_iif.h`, common entity pad helpers, and IIF route handling in `vsp1_entity_route_setup()` where IIF shares the BRU route with selector bits.

Risks and test signals: risks include route selector mistakes, metadata pad code handling through generic helpers, and unsupported exposure to userspace. Test VSPX pipeline construction, format propagation on all three pads, and display-list register output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_iif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_iif.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_iif.h

Purpose: declares the VSPX ISP Interface entity wrapper and pad indexes.

Important APIs and types: defines `VSPX_IIF_SINK_PAD_IMG`, `VSPX_IIF_SINK_PAD_CONFIG`, `struct vsp1_iif`, `to_iif()`, and `vsp1_iif_create()`. The structure only embeds `struct vsp1_entity`.

Control flow role: used by `vsp1_drv.c` to instantiate IIF on VSPX Gen4 variants and by VSPX/IIF configuration code to access the entity.

State and persistence: all state is inherited from the embedded entity: pad formats, media links, route, and pipeline membership.

Dependencies and integration: includes V4L2 subdev and common entity declarations.

Risks and test signals: pad constants must stay aligned with the hardware and with any VSPX code that references image versus config inputs. Test VSPX graph/pipeline setup and compile coverage for IIF-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_iif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lif.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lif.c

Purpose: implements the LCD Controller Interface entity used by internal DRM display pipelines. It configures LIF output thresholds and enables the LIF block that feeds the display unit.

Important APIs and functions: `vsp1_lif_create()` and `lif_configure_stream()`. Generic entity pad handlers provide format enumeration and setting for ARGB/AYUV.

Control flow: constructor creates an internal two-pad entity with the LIF index and format/dimension limits. During stream configuration, the source pad format is read and generation/model-specific threshold values are selected. The code writes `VI6_LIF_CSBTH`, `VI6_LIF_CTRL`, and on non-zero-LBA variants `VI6_LIF_LBA`.

State and persistence: persistent state is mostly the embedded entity plus index. Threshold programming is recomputed at stream configuration and stored in display-list entries. There are no controls.

Dependencies and integration: depends on display-list writes, entity helpers, VSP1 version/feature flags, and DRM setup in `vsp1_drm.c`, which attaches WPF output to LIF and verifies final format.

Risks and test signals: risks include model-specific threshold mistakes, suspicious `format->code == 0` CFMT check, LIF index register offset errors, and LBA quirk regressions. Test display output on Gen2/Gen3/Gen4/RZ/G2L variants, interlaced/progressive modes, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lif.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lif.h

Purpose: declares the LIF entity wrapper used by DRM display pipelines.

Important APIs and types: defines `LIF_PAD_SINK`, `LIF_PAD_SOURCE`, `struct vsp1_lif`, `to_lif()`, and `vsp1_lif_create()`. `struct vsp1_lif` embeds only the common `vsp1_entity`.

Control flow role: `vsp1_drv.c` creates LIF entities only for non-UAPI display use. `vsp1_drm.c` attaches each pipeline's WPF to its LIF and calls subdev pad operations before entity stream configuration.

State and persistence: all mutable state is held by the embedded entity and its active subdev state.

Dependencies and integration: includes media entity/V4L2 subdev and common entity declarations.

Risks and test signals: LIF index and pad constants must match DRM setup. Test all LIF counts declared in `vsp1_device_info` and dual-pipeline devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lut.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lut.c

Purpose: implements the VSP1 1D look-up table processor. It exposes a 256-entry U32 V4L2 control, enables the LUT hardware, and injects table writes into display lists.

Important APIs and functions: `vsp1_lut_create()`, `lut_set_table()`, `lut_s_ctrl()`, `lut_configure_stream()`, `lut_configure_frame()`, and `lut_destroy()`. Supported media bus codes are ARGB, AHSV, and AYUV 32-bit formats.

Control flow: table control updates allocate a display-list body, write all `VI6_LUT_TABLE + 4*i` entries, swap the pending body under a spinlock, and drop the local reference. Stream configuration writes `VI6_LUT_CTRL_EN`. Per-frame configuration consumes any pending table body by adding it to the current display list and releasing the local reference.

State and persistence: `struct vsp1_lut` stores control handler, spinlock, pending table body, and body pool. LUT table updates persist as DMA-backed display-list entries rather than direct register writes. The pool has three bodies to tolerate queued/pending hardware updates.

Dependencies and integration: depends on V4L2 custom controls, common entity pad helpers, display-list body pools, and route setup. Created only on feature-enabled variants.

Risks and test signals: risks include pool exhaustion on rapid updates, update coalescing through swap semantics, and table payload validation. Test control updates while streaming, graph insertion/removal, visual LUT effect, and cleanup under active queued lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lut.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lut.h

Purpose: declares private state for the VSP1 1D LUT entity.

Important APIs and types: defines `LUT_PAD_SINK`, `LUT_PAD_SOURCE`, `struct vsp1_lut`, `to_lut()`, and `vsp1_lut_create()`. The structure embeds the common entity, a V4L2 control handler, spinlock, pending LUT display-list body, and body pool.

Control flow role: entity creation and subdev callbacks convert from `v4l2_subdev` to `vsp1_lut` with `to_lut()`. The pending body and pool fields are used to hand table updates from control context to frame configuration.

State and persistence: control state is handled by the V4L2 control core; pending table programming persists in `lut` until consumed. The body pool owns DMA memory for table register writes.

Dependencies and integration: includes spinlock, media entity, V4L2 controls/subdev, and common entity declarations.

Risks and test signals: changes must preserve lock-protected table handoff. Test LUT control updates, stream configuration, and entity cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_lut.h -->
