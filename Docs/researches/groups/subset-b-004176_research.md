# subset-b-004176 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vip.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vip.c

Purpose: TI VIP capture driver for DRA7-style Video Input Port hardware. It registers V4L2 capture nodes for graph-connected sensors, configures parser/scaler/CSC datapaths, manages vb2 DMA-contig queues, builds VPDMA descriptor lists, and recovers from parser FIFO overflow conditions.

Important APIs/types/functions: `vip_formats[]` maps supported V4L2 fourcc/media-bus codes to VPDMA formats. `vip_querycap()`, format, selection, standard, streamparm, and buffer ioctls provide the user ABI. `vip_video_qops` implements vb2 setup/prepare/queue/start/stop. `vip_start_streaming()` and `vip_stop_streaming()` are the main stream lifecycle. `add_out_dtd()`, `populate_desc_list()`, `start_dma()`, `vip_schedule_next_buffer()`, and `vip_process_buffer_complete()` drive descriptor reuse and buffer completion. Probe flow is `vip_probe()` -> `vip_probe_slice()` -> asynchronous VPDMA firmware callback `vip_vpdma_fw_cb()` -> `vip_probe_complete()` -> fwnode notifier binding.

Control flow: probe rejects devices with no OF graph endpoints, enables runtime PM, validates the VIP PID, creates two slice devices, maps parser/scaler/CSC offsets, initializes VPDMA, and waits for firmware before scanning endpoints. When a subdevice binds, the driver enumerates media bus codes, filters usable local formats, allocates one capture stream, registers a video node, and allocates a VPDMA hardware-list slot. On first open it initializes hardware clocks, queries the subdevice active format, allocates coefficient/MMR ADB buffers, and creates the stream descriptor list. `S_FMT` negotiates a source subdevice size, decides scaler/CSC allocation, stores crop and frame geometry, and programs the subdevice format. `start_streaming()` uploads scaler/CSC config, routes datapath registers, configures the parser, starts the upstream subdevice, primes two buffers into VPDMA, enables interrupts, schedules another buffer or drop buffer, and enables the parser. IRQ handling clears parser/list status, completes the posted buffer, schedules the next buffer, and acknowledges EOI. Parser overflow disables IRQs and schedules work that stops the parser, resets parser/datapath/VPDMA state, requeues active buffers, reloads descriptors, and re-enables capture up to a recovery limit.

State and persistence: persistent runtime state is split across `struct vip_shared`, per-slice `struct vip_dev`, per-input `struct vip_port`, and per-video-node `struct vip_stream`. Port state tracks endpoint flags, active formats, crop, current format, scaler/CSC ownership, shadow MMR ADB, and coefficient buffers. Stream state tracks current field/sequence, vb2 queue, software queues (`vidq`, `dropq`, `post_bufs`), VPDMA list number, descriptor list, write-back descriptor pointer, used channel bitmap, and recovery work. Hardware-visible state is carried in VIP top/parser/datapath registers, VPDMA CSTAT/list state, and mapped descriptor/config buffers.

Dependencies and integration: depends on V4L2 core, V4L2 async/fwnode graph binding, vb2 DMA-contig, runtime PM, syscon/regmap for pixel-clock polarity, TI VPDMA helpers, scaler helpers from `sc.c`, CSC helpers from `csc.c`, and register definitions in `vpe_regs.h`/`vip.h`. It integrates with DT compatible `ti,dra7-vip`, upstream sensor subdevices, and the shared VPDMA firmware `vpdma-1b8.bin`.

Risks: `vip_stop_streaming()` has unreachable descriptor unmap/reset code after `return_buffers()`, so descriptor state relies on later release/recovery paths. `vip_release_stream()` calls `vpdma_free_desc_buf(&stream->desc_list.buf)` and then `vpdma_free_desc_list(&stream->desc_list)`, which also frees the same buffer. FIFO recovery assumes one active stream per port when selecting a stream from `cap_streams[]`. Descriptor list sizing and `stream->write_desc = base + 15` rely on fixed descriptor ordering. `vpdma_hwlist_release()` behavior in the helper may affect IRQ-to-stream private lookup if releases/reallocations occur. RAW8 is represented through a fake 16-bit VPDMA format and width halving, so parser/VPDMA size math is fragile.

Test signals: build with `CONFIG_VIDEO_TI_VIP` and `CONFIG_VIDEO_TI_VPE_DEBUG`; boot probe with `ti,dra7-vip`, `ti,ctrl-module`, two IRQs, VPDMA firmware, and graph endpoints; `v4l2-ctl --list-formats-ext`, `S_FMT` with YUV/RGB/raw and crop changes; capture with mmap and dmabuf; no-buffer drop queue operation; parser FIFO overflow recovery logs; subdevice stream on/off sequencing; and remove/unbind without descriptor buffer warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vip.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vip.h

Purpose: private header for the TI VIP capture driver. It defines the VIP data model, constants, resource ownership fields, stream queues, media-bus format mapping, and parser/scaler/CSC/VPDMA integration state used by `vip.c`.

Important APIs/types: `enum vip_csc_state` describes CSC availability/direction. `struct vip_buffer` wraps `vb2_v4l2_buffer` with driver queue/drop state. `struct vip_fmt` maps V4L2 pixel formats to media-bus codes and VPDMA per-plane formats. `struct vip_shared` owns common VPDMA and V4L2 state shared by slices. `struct vip_dev` represents one VIP slice with parser/scaler/CSC resources and IRQ. `struct vip_port` represents port A/B, endpoint, crop, active formats, shadow MMR/coeff buffers, and scaler/CSC allocation. `struct vip_stream` owns one video node, VPDMA list number, vb2 queue, buffer queues, descriptor list, and recovery state.

Control flow: `vip.c` includes this header before building all probe, format, streaming, and interrupt paths. Probe allocates `vip_shared`, two `vip_dev` instances, then ports and streams. Open/close use the port and stream counters to power resources up/down. Streaming updates the fields declared here and passes embedded VPDMA buffers to the helper library.

State and persistence: this header documents all long-lived driver state. The key persistent handles are MMIO bases, `struct vpdma_data`, `struct v4l2_device`, async notifiers, endpoint metadata, per-port allocated coefficient/MMR buffers, per-stream VPDMA channel bitmaps, and queues. No on-disk persistence exists.

Dependencies and integration: includes Linux video/V4L2/vb2/fwnode/async headers plus `vpdma.h`, `vpdma_priv.h`, `sc.h`, and `csc.h`. The constants tie VIP slices, ports, VPDMA channels, and CFD client IDs together.

Risks: it exposes internal layout tightly coupled to descriptor ordering and hardware channel numbering. `VIP_MAX_ACTIVE_FMT` must stay synchronized with `vip_formats[]`. The header includes `vpdma_priv.h`, so VIP code depends on private descriptor/register details, not only the public VPDMA API. Resource assignment fields (`sc_assigned`, `csc_assigned`) are integer port IDs with no separate locking beyond the device mutex expectations.

Test signals: compile coverage for `CONFIG_VIDEO_TI_VIP`; format enumeration count matching `VIP_MAX_ACTIVE_FMT`; two-slice/two-port probe; scaler and CSC allocation/free across repeated open/S_FMT/close; and async notifier cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma.c

Purpose: helper library for TI VPDMA, shared by VPE mem2mem and VIP capture. It defines hardware data-format tables, allocates/maps descriptor buffers, builds data/config/control descriptors, submits descriptor lists, manages VPDMA list interrupt bits and hardware-list slots, programs client CSTAT fields, dumps registers, and uploads VPDMA firmware.

Important APIs: exported format tables `vpdma_yuv_fmts`, `vpdma_rgb_fmts`, `vpdma_raw_fmts`, and `vpdma_misc_fmts`; buffer helpers `vpdma_alloc_desc_buf()`, `vpdma_free_desc_buf()`, `vpdma_map_desc_buf()`, `vpdma_unmap_desc_buf()`; list helpers `vpdma_create_desc_list()`, `vpdma_reset_desc_list()`, `vpdma_free_desc_list()`, `vpdma_submit_descs()`, `vpdma_list_busy()`, `vpdma_update_dma_addr()`, and `vpdma_list_cleanup()`; descriptor builders `vpdma_add_cfd_block()`, `vpdma_add_cfd_adb()`, `vpdma_add_sync_on_channel_ctd()`, `vpdma_add_abort_channel_ctd()`, `vpdma_add_out_dtd()`, `vpdma_rawchan_add_out_dtd()`, and `vpdma_add_in_dtd()`; interrupt/config helpers `vpdma_enable_list_complete_irq()`, `vpdma_clear_list_stat()`, `vpdma_set_line_mode()`, `vpdma_set_frame_start_event()`, `vpdma_set_max_size()`, and `vpdma_set_bg_color()`; initialization through `vpdma_create()`/`vpdma_load_firmware()`.

Control flow: clients create a descriptor list backed by a kzalloc buffer, append CFD/CTD/DTD structures by advancing `list->next`, map the list for DMA, then submit by writing `VPDMA_LIST_ADDR` and `VPDMA_LIST_ATTR` under the VPDMA spinlock. Data descriptor builders calculate plane offsets from crop rectangles, line stride, depth, chroma subsampling, direction, channel, and flags. `vpdma_update_dma_addr()` lets VIP reuse an already-built descriptor list by unmapping, patching start and descriptor write-back addresses, and remapping. Cleanup stops a hardware list and optionally posts abort-channel CTDs for every active channel. Firmware loading is asynchronous: `request_firmware_nowait()` calls `vpdma_firmware_cb()`, copies `vpdma-1b8.bin` into a DMA buffer, writes the firmware list address, polls LIST_RDY, then invokes the client callback.

State and persistence: `struct vpdma_data` persists base MMIO, platform device, spinlock, hardware-list allocation bitmap, per-list private pointers, and firmware callback. `struct vpdma_buf` persists CPU pointer, DMA address, size, and mapped flag for each descriptor/config payload. Hardware state persists in VPDMA list, CSTAT, interrupt mask/status, max-size, and background-color registers until reset or overwritten.

Dependencies and integration: uses Linux DMA mapping, firmware loading, platform resources, MMIO accessors, and video format definitions. It consumes private register/descriptor macros from `vpdma_priv.h` and public contracts from `vpdma.h`. `vpe.c` and `vip.c` call it for all VPDMA descriptor submission and list interrupt control.

Risks: descriptor buffers are allocated with `kzalloc()` and only WARN on alignment; DMA descriptor hardware may require stricter alignment than slab allocation guarantees. `vpdma_hwlist_release()` stores `priv = vpdma->hwlist_priv` rather than `vpdma->hwlist_priv[list_num]`, so callers expecting the released private pointer may get the array address. `vpdma_update_dma_addr()` recalculates write-back addresses using `list->buf.dma_addr` while the buffer is unmapped; DMA API implementations generally leave the old DMA address stored, but the sequencing is subtle. Busy waits in cleanup use a tight loop without sleep. Firmware callback failure paths do not call the client callback, so dependent video nodes may never register if firmware load fails.

Test signals: module build/export resolution for TI VPE/VIP; firmware present at `vpdma-1b8.bin`; register traces showing LIST_RDY after firmware upload; descriptor-list submission/completion interrupts; DMA mapping debug with map/unmap balance; VPE and VIP streaming through both packed and coplanar formats; channel abort cleanup after streamoff/recovery; and debug dumps for VPDMA CSTAT/list registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma.h

Purpose: public VPDMA helper API and shared format/channel contract for TI VPE/VIP drivers. It exposes descriptor buffer/list state, VPDMA format tables, channel identifiers, descriptor flags, ADB helpers, list management, descriptor builders, interrupt helpers, client configuration, and VPDMA initialization.

Important APIs/types: `struct vpdma_buf`, `struct vpdma_desc_list`, and `struct vpdma_data` are the core state carriers. `struct vpdma_data_format` describes hardware data type/depth for YUV, RGB, raw, and misc formats. `enum vpdma_channel` names the VPE channels also reused by VIP output channel mapping. `VPDMA_SET_MMR_ADB_HDR()` and related macros fill address-data-block headers for register writes. Function prototypes cover buffer map/unmap, descriptor list submit/reuse/cleanup, hardware-list allocation, CFD/CTD/DTD emission, list IRQ masking/status, CSTAT line/frame-start programming, max-size/background configuration, register dump, and firmware/create.

Control flow: clients include this header, allocate a `struct vpdma_data`, initialize it with `vpdma_create()` or `vpdma_load_firmware()`, allocate descriptor/config buffers, append descriptors using the builder APIs, submit lists, and clear/listen for list-complete interrupts. VIP additionally uses hardware-list slots to map VPDMA list numbers back to `struct vip_stream`.

State and persistence: the header makes explicit which software state must survive across submissions: descriptor buffers must not be freed while mapped, `list->next` tracks append position, `hwlist_used[]` and `hwlist_priv[]` persist list ownership, and firmware callback state persists in `vpdma_data`.

Dependencies and integration: includes no large framework headers itself, but prototypes use DMA addresses, `platform_device`, V4L2 rectangles, and VPDMA private channel/client concepts. It is the shared ABI between `vpdma.c`, `vpe.c`, and `vip.c`.

Risks: channel constants mix VPE enum IDs with VIP raw channel offsets, so users must distinguish enum channel inputs from raw numeric channel inputs. `VPDMA_MAX_CHANNELS` is large enough for bitmap-style arrays but not type-safe. Descriptor and stride alignments are compile-time constants that callers must honor before hardware submission. ADB helper macros use pointer arithmetic through typed null pointers and require payload subblocks to be 16-byte aligned by the caller.

Test signals: compile all TI VPE/VIP users, check exported symbol availability when `CONFIG_VIDEO_TI_VPDMA=m`, run descriptor list creation/submission paths, validate packed/coplanar/raw format table indexing, and verify VPDMA list allocation/release under repeated video node registration/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma_priv.h

Purpose: private VPDMA register and descriptor layout header. It defines MMIO offsets, interrupt register layout, client CSTAT fields, hardware data type values, raw channel numbers, and inline pack/unpack helpers for data transfer, configuration, and control descriptors.

Important APIs/types: top-level register macros cover `VPDMA_LIST_ADDR`, `VPDMA_LIST_ATTR`, list status, background colors, max size registers, channel/client/list interrupt status/mask, and VPE/VIP client CSTAT offsets. Hardware data type macros encode YUV, RGB, raw-reused, and motion-vector formats. `struct vpdma_dtd`, `struct vpdma_cfd`, and `struct vpdma_ctd` model data transfer, configuration, and control descriptors. Inline helpers such as `dtd_type_ctl_stride()`, `dtd_pkt_ctl()`, `dtd_desc_write_addr()`, `cfd_pkt_payload_len()`, and `ctd_type_source_ctl()` compose descriptor words; paired getters support debug dumps.

Control flow: `vpdma.c` uses this header to translate high-level helper calls into descriptor words and register fields. `vpe.c` and `vip.c` include it indirectly/directly where they need private VPDMA constants such as max-size registers and raw channel numbers.

State and persistence: no dynamic software state is stored here. The file describes persistent hardware state in VPDMA registers and the in-memory descriptor ABI consumed by the VPDMA list parser.

Dependencies and integration: used by the VPDMA helper implementation and by TI VPE/VIP clients. It integrates the driver with documented VPDMA descriptor packet types, control descriptor operations, data type mappings, and hardware channel numbering.

Risks: any bitfield or channel-number drift from the hardware TRM/errata silently corrupts DMA programming. Some getter helpers reuse masks in ways that should be reviewed, such as `ctd_get_fid0_ctl()` masking with `CTD_FID2_MASK`. Several fields are packed by shifts without explicit masking in setter helpers, relying on callers to pass bounded values. Descriptor structs assume the compiler layout matches the hardware 32-bit word sequence.

Test signals: compile coverage plus dynamic debug descriptor dumps; VPDMA register traces for max size, list attr, CSTAT, and interrupt masks; DMA transfers for every supported YUV/RGB/raw/motion-vector data type; and hardware tests that exercise sync-on-channel and abort-channel CTDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpe.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpe.c

Purpose: TI VPE V4L2 mem2mem driver. It exposes a multi-plane M2M video node that scales, color-converts, converts chroma formats, and optionally deinterlaces frames by programming the VPE datapath and submitting VPDMA descriptor lists.

Important APIs/types/functions: `struct vpe_dev` is the singleton hardware device; `struct vpe_ctx` is a per-open m2m context with source/destination queue data, descriptor/config buffers, MV buffers, deinterlacing state, and current job state; `struct vpe_q_data` stores current format/crop/compose and interlace flags. `vpe_ioctl_ops` implements format, selection, streaming, and buffer ioctls. `m2m_ops` connects `device_run()`, `job_ready()`, and `job_abort()` to V4L2 mem2mem. Hardware configuration is built by `set_src_registers()`, `set_dst_registers()`, `set_srcdst_params()`, `set_dei_regs()`, `set_cfg_modes()`, and `config_edi_input_mode()`. Descriptor assembly is in `add_in_dtd()`, `add_out_dtd()`, and `device_run()`. Completion is in `vpe_irq()`.

Control flow: probe coerces 32-bit DMA, registers the V4L2 device, maps the `vpe_top` resource, requests IRQ, initializes the m2m device, enables runtime PM/clocks, resets top/VPDMA blocks, creates scaler/CSC helpers, initializes VPDMA, and registers the video node from the VPDMA firmware callback. Open allocates a context, descriptor list, MMR ADB, scaler coefficient buffers, default 1080p YUYV source/destination formats, controls, and m2m queues. `S_FMT` validates VPDMA stride/plane constraints, updates interlace flags, updates source/destination shadow registers, allocates motion-vector buffers when interlaced-to-progressive deinterlacing is needed, computes CSC/scaler coefficients, and marks MMRs dirty. `device_run()` removes/peeks source buffers according to field mode, removes a destination buffer, emits dirty config descriptors and coefficient downloads, emits output/input DTDs and sync CTDs, enables interrupts, maps the list, and submits VPDMA list 0. `vpe_irq()` clears VPE/VPDMA status, handles DEI/downsampler warnings, unmaps config/list buffers, rotates MV ping-pong buffers, copies source metadata to destination, completes buffers, shifts retained deinterlacing source fields, and either chains another buffer in the same job or finishes the m2m job.

State and persistence: global state includes VPE MMIO base, VPDMA/scaler/CSC handles, loaded MMR DMA address cache, IRQ, m2m device, instance count, and locks. Per-context state persists queue formats/crop/compose, field/sequence, batch size, in-flight source/destination buffers, dirty MMR flag, descriptor list, coefficient/MMR buffers, deinterlacing flag, and two coherent motion-vector buffers whose roles alternate after each field.

Dependencies and integration: depends on V4L2 mem2mem, vb2 DMA-contig, runtime PM, platform resources/IRQs, TI VPDMA helpers, scaler and CSC helper modules, and `vpe_regs.h` register definitions. It binds to DT compatible `ti,dra7-vpe` and requires VPDMA firmware registration before exposing `/dev/video*`.

Risks: `__vpe_s_fmt()` stores `q_data->format = *f` before reading `qpix->field`, so interlace flag updates inspect the previous stored format rather than the new `pix->field`. `realloc_mv_buffers()` frees old buffers before allocating new ones; if the first or second allocation fails, pointers/size can describe freed memory until overwritten. `device_run()` emits both luma and chroma input DTDs unconditionally, which relies on format/descriptor handling tolerating non-coplanar chroma entries. `vpe_start_streaming()` returns queued buffers for only the queue being started on size failure. Hardware list 0 is shared globally, so m2m serialization must prevent concurrent submissions. Correct deinterlacing depends on subtle source buffer retention and SEQ_TB/SEQ_BT field toggling.

Test signals: build with `CONFIG_VIDEO_TI_VPE`/`CONFIG_VIDEO_TI_VPDMA`; firmware callback registering the VPE video node; `v4l2-compliance` for mem2mem multiplanar queues; format tests for NV12/NV16/NV21/YUYV/UYVY/RGB outputs; crop/compose scaling within `SC_MAX_PIXEL_*`; interlaced alternate and SEQ_TB/SEQ_BT deinterlacing with enough source buffers; IRQ list-complete handling; streamoff while a job is in flight; and PM probe/remove cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpe_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpe_regs.h

Purpose: register map and bitfield definitions for the TI VPE/VIP top-level blocks used by the VPE mem2mem and VIP capture drivers. It names PID, interrupt, clock/reset, datapath format/select, upsampler, DEI, EDI, and film-mode-detection registers.

Important APIs/types: this header exports macros only. Key groups include `VPE_PID_*` extraction fields, `VPE_INT0_*` list/client/error interrupt bits, `VPE_CLK_ENABLE`/`VPE_CLK_RESET` and clock bits, `VPE_CLK_FORMAT_SELECT` datapath fields (`VPE_RGB_OUT_SELECT`, `VPE_DS_SRC_DEI_SCALER`, `VPE_CSC_SRC_DEI_SCALER`, `VPE_DS_BYPASS`, `VPE_COLOR_SEPARATE_422`), chroma upsampler register offsets/fields, DEI frame-size/bypass/flush/progressive bits, EDI configuration/LUT fields, and FMD window/control/status fields.

Control flow: `vpe.c` composes shadow MMR ADB payloads using these offsets and fields, then uploads them through VPDMA. `vip.c` also uses VIP/VPE top-level clock/reset/datapath constants while configuring slice paths and interrupts. The values determine which hardware subblocks are clocked, reset, routed, and interrupted.

State and persistence: no software state is stored here. The macros describe persistent MMIO state in the hardware until reset or reprogrammed by VPE/VIP.

Dependencies and integration: depends on `BIT()` being available from included kernel headers in users. It is integrated with `vpe.c`, `vip.c`, and scaler/CSC register offsets used in ADB construction.

Risks: duplicated macro names in the upsampler/EDI blocks can hide accidental redefinition drift. A typo-like `VPE_INTC_EOI` versus the VIP code’s `VIP_INTC_E0I` usage should be watched in compile coverage. Register-field changes are not type-checked, so wrong masks/shifts would produce valid builds but invalid hardware programming.

Test signals: compile coverage for VPE and VIP users; register dump comparison against the DRA7 TRM; successful VPE scaling/deinterlacing and VIP capture datapath routing; interrupts firing and clearing on expected list/error bits; and reset/clock sequencing across runtime PM cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpe_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/Kconfig

Purpose: Kconfig menu for Verisilicon/Hantro media platform drivers. It defines the main Hantro VPU driver option and SoC/feature suboptions that select which hardware integration files are built.

Important symbols: `VIDEO_HANTRO` is a tristate for the `hantro-vpu` module and depends on supported SoC architecture families or `COMPILE_TEST`, `V4L_MEM2MEM_DRIVERS`, and `VIDEO_DEV`; it selects media controller, vb2 DMA-contig/vmalloc, V4L2 mem2mem, and codec helper support for H.264, JPEG, and VP9. `VIDEO_HANTRO_HEVC_RFC` enables optional HEVC reference-frame compression. `VIDEO_HANTRO_IMX8M`, `VIDEO_HANTRO_SAMA5D4`, `VIDEO_HANTRO_ROCKCHIP`, `VIDEO_HANTRO_SUNXI`, and `VIDEO_HANTRO_STM32MP25` are bool SoC support toggles depending on `VIDEO_HANTRO` plus their architecture or `COMPILE_TEST`.

Control flow: kernel configuration enables `VIDEO_HANTRO`, which pulls in common Hantro mem2mem codec code. Per-SoC bools default to `y` when the main driver is enabled and their architecture dependency is satisfied, causing the Makefile to include hardware description/integration objects for that platform.

State and persistence: no runtime state; this file controls build-time inclusion and module availability.

Dependencies and integration: integrates the Verisilicon driver directory with V4L2 mem2mem, media controller, videobuf2, codec control helpers, and architecture-specific platform support. Its symbols are consumed by the sibling Makefile.

Risks: default-`y` SoC suboptions can broaden compile coverage and module size whenever `VIDEO_HANTRO` is enabled. Codec capabilities depend on selected helpers staying aligned with source files in the Makefile; for example AV1 Rockchip objects are built under Rockchip support even though the main symbol help text focuses on broader VPU encode/decode support. HEVC RFC changes memory/bandwidth behavior and should be tested separately.

Test signals: `olddefconfig`/`allmodconfig`/`COMPILE_TEST` coverage; module build as built-in and module; per-SoC configs selecting the expected objects; and runtime probe on i.MX8M, SAMA5D4, Rockchip, Sunxi H6, and STM32MP25 platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/Makefile

Purpose: object composition rules for the Verisilicon/Hantro VPU media driver. It builds the `hantro-vpu` composite object from common codec/framework files and appends SoC-specific hardware integration files according to Kconfig symbols.

Important entries: `obj-$(CONFIG_VIDEO_HANTRO) += hantro-vpu.o` creates the main module/built-in object. `hantro-vpu-y` always includes common driver, V4L2, postprocessor, JPEG encoder, G1/G2 codec engines, H.264/MPEG2/VP8/HEVC/VP9 helpers, and JPEG helpers. Conditional lists add `imx8m_vpu_hw.o`, `sama5d4_vdec_hw.o`, Rockchip JPEG/H.264/MPEG2/VP8/AV1/filmgrain/entropy/hardware files, `sunxi_vpu_hw.o`, and `stm32mp25_vpu_hw.o`.

Control flow: Kbuild uses the `VIDEO_HANTRO` tristate to decide whether `hantro-vpu.o` is linked. It then folds each `hantro-vpu-y` and `hantro-vpu-$(CONFIG_...)` object into the composite driver for the selected configuration.

State and persistence: no runtime state; it controls build artifacts and link composition.

Dependencies and integration: pairs directly with `verisilicon/Kconfig` and the parent media platform build. The common object list must stay in sync with codec support selected by `VIDEO_HANTRO`; conditional objects must match SoC support symbols.

Risks: missing a new codec/helper object from the common list can cause unresolved symbols or silently absent format support. Rockchip support gathers several generations and AV1 support under one config symbol, so platform-specific code can be compiled on Rockchip builds even when not used by the running SoC. Object ordering is conventional but common files must provide symbols before SoC hooks reference them at link time.

Test signals: `make M=drivers/media/platform/verisilicon` under each config combination; `modinfo hantro-vpu` when modular; link checks for all conditional SoC symbols; and boot probe on each supported platform confirming the expected hardware variant table is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/verisilicon/Makefile -->
