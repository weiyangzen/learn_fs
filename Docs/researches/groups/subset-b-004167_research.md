# subset-b-004167 research

Grouped research report for the requested Samsung S5P MFC encoder/operation files and STMicroelectronics media platform BDISP build/debug files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_enc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_enc.c

Purpose: implements the V4L2 mem2mem encoder side of the Samsung S5P MFC driver. It exposes supported raw and compressed formats, encoder controls, V4L2 ioctl callbacks, vb2 queue operations, and codec callbacks that bridge userspace buffer flow to the hardware operation table.

Important APIs and functions: exported accessors are `get_enc_codec_ops`, `get_enc_queue_ops`, `get_enc_v4l2_ioctl_ops`, `s5p_mfc_enc_ctrls_setup`, `s5p_mfc_enc_ctrls_delete`, and `s5p_mfc_enc_init`. Main local entry points are `find_format`, `s5p_mfc_ctx_ready`, `enc_pre_seq_start`, `enc_post_seq_start`, `enc_pre_frame_start`, `enc_post_frame_start`, all `vidioc_*` operations, `s5p_mfc_enc_s_ctrl`, `s5p_mfc_enc_g_v_ctrl`, and vb2 callbacks from `s5p_mfc_queue_setup` through `s5p_mfc_buf_queue`. The static `formats[]` table maps source raw formats and destination codecs to MFC version bits, while `controls[]` defines H.264, MPEG4, H.263, VP8, HEVC, rate-control, frame-skip, slice, padding, and volatile minimum-buffer controls.

Control flow: `s5p_mfc_enc_init` installs default NV12M input and H.264 output formats. Userspace enumerates, tries, and sets formats through the ioctl table; raw output format updates image dimensions and triggers `enc_calc_src_size`, while compressed capture format sets codec mode and stream-buffer sizing. `REQBUFS`, `QBUF`, `DQBUF`, `EXPBUF`, `STREAMON`, and `STREAMOFF` mostly delegate to vb2 but maintain MFC queue state and context readiness. When both destination and source conditions satisfy `s5p_mfc_ctx_ready`, the code sets the context work bit and calls `try_run`. Sequence start programs the compressed stream buffer; sequence completion either completes a standalone header buffer on older hardware or records required reference-buffer/scratch sizes on v6+ and moves to `MFCINST_HEAD_PRODUCED`. Per-frame start programs source and destination DMA addresses. Per-frame completion matches the encoded source address back to queued or reference source buffers, completes encoded destination buffers with payload size and key/P/B flags, moves used source buffers to `ref_queue`, and clears scheduling when input or output is exhausted.

State and persistence: all state is per `struct s5p_mfc_ctx` and volatile. It tracks source/destination format pointers, image dimensions, plane sizes and strides, encoded destination size, queue counters, `src_queue`, `dst_queue`, `ref_queue`, state machine values, encoder parameters, codec-specific control values, and vb2 buffer cookies. V4L2 controls persist only for the lifetime of the file/context. No data is persisted outside driver memory and hardware registers.

Dependencies and integration points: depends on V4L2 ioctl/control/event APIs, videobuf2-v4l2 and DMA-contig helpers, MFC common state, interrupt waiting, debug macros, and version-specific hardware ops via `s5p_mfc_hw_call`. It integrates with the core MFC scheduler through context work bits, `dev->irqlock`, `dev->mfc_ops->try_run`, and interrupt-driven post callbacks. It also publishes `V4L2_EVENT_EOS` subscription and handles `V4L2_ENC_CMD_STOP` for end-of-stream.

Risks: state checks are strict and can return `-EINVAL` or `-EBUSY` for userspace sequences that set formats or request buffers after streaming has progressed. `vidioc_g_parm` checks `V4L2_BUF_TYPE_VIDEO_OUTPUT` rather than the multi-plane type used elsewhere, which is a compatibility risk. The source-completion path matches buffers by DMA addresses; duplicated or recycled DMA addresses would make diagnostics difficult. HEVC QP range updates mutate control min/max dynamically and need control-handler correctness. Several controls are accepted even when later hardware generations or codec modes ignore them. Stop-streaming can wait for firmware frame completion while holding higher-level stream teardown context, so firmware timeout behavior matters.

Test signals: build with MFC encoder support across v5, v6/v7, v10, and v12 configurations; `v4l2-compliance` for multi-plane mem2mem encode nodes; encode smoke tests for H.264, MPEG4, H.263, VP8, and HEVC where supported; buffer lifecycle tests for `STREAMON`, `STREAMOFF`, EOS command, empty input buffers, and header-only mode; control get/set tests including volatile `V4L2_CID_MIN_BUFFERS_FOR_OUTPUT`; DMA-BUF and MMAP queue coverage; and hardware traces confirming payload sizes, keyframe flags, and EOS event behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_enc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_enc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_enc.h

Purpose: declares the public encoder-side hooks exported by `s5p_mfc_enc.c` to the S5P MFC core.

Important APIs and types: exposes accessor functions for `struct s5p_mfc_codec_ops`, `struct vb2_ops`, and `struct v4l2_ioctl_ops`, plus encoder control lifecycle helpers `s5p_mfc_enc_ctrls_setup` and `s5p_mfc_enc_ctrls_delete`, and default-format initializer `s5p_mfc_enc_init`.

Control flow: the core MFC probe/open path includes this header, initializes a context with `s5p_mfc_enc_init`, installs V4L2 controls through `s5p_mfc_enc_ctrls_setup`, and binds the returned ioctl/vb2/codec operation tables to the encoder video device and context.

State and persistence: no state is stored in the header. All functions operate on caller-owned `struct s5p_mfc_ctx` or return static operation tables owned by the implementation.

Dependencies and integration points: relies on consumers already knowing `struct s5p_mfc_ctx`, `struct s5p_mfc_codec_ops`, `struct vb2_ops`, and `struct v4l2_ioctl_ops` through MFC and media headers. It is the narrow integration boundary between generic MFC context setup and the encoder implementation.

Risks: the header does not include or forward-declare the referenced structures, so include ordering must provide type declarations. ABI expectations are internal to the kernel driver but mismatched table lifetimes or missing setup/cleanup calls would leak controls.

Test signals: compile coverage of MFC encoder registration and context open/close paths; control handler leak checks on repeated open/close; and link coverage proving the exported functions are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_enc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_intr.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_intr.c

Purpose: provides wait helpers for MFC firmware command completion at device and context scope.

Important APIs and functions: `s5p_mfc_wait_for_done_dev` waits on `dev->queue` for a device interrupt type matching the requested command or an error return. `s5p_mfc_wait_for_done_ctx` does the same for `ctx->queue`, using either interruptible or non-interruptible waits according to its `interrupt` argument. `s5p_mfc_clean_dev_int_flags` and `s5p_mfc_clean_ctx_int_flags` clear interrupt condition, type, and error fields.

Control flow: callers clear flags before issuing firmware commands, then wait until the interrupt handler sets `int_cond` and `int_type` and wakes the queue. Timeout uses `MFC_INT_TIMEOUT`; timeout, signal interruption, or firmware error return all map to a nonzero failure result. Successful matching commands return zero.

State and persistence: state is transient interrupt state in `struct s5p_mfc_dev` and `struct s5p_mfc_ctx`: `int_cond`, `int_type`, and `int_err`. The helpers do not touch hardware registers directly and do not persist state beyond clearing these fields.

Dependencies and integration points: depends on Linux wait queues, timeout conversion, errno values, and MFC debug/common definitions. It is used by command, scheduler, stream-on/off, and volatile-control paths that need synchronous confirmation from the firmware after an asynchronous hardware command.

Risks: all failure modes return `1`, so callers cannot distinguish timeout, signal, or firmware error without logs and saved `int_err`. A stale interrupt flag can satisfy a later wait unless the caller cleaned flags first. The interruptible path only handles `-ERESTARTSYS`, while other negative wait returns would be treated as success if ever introduced. Timeout-sensitive paths depend on firmware, clock, and IRQ delivery.

Test signals: fault-injection tests for no interrupt, error interrupt, and signal interruption; hardware tests around open instance, sequence done, frame done, sleep/wake, and abort; and lockdep/runtime tests ensuring waits are not made from atomic context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_intr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_intr.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_intr.h

Purpose: declares the MFC interrupt wait and interrupt-flag cleanup helpers.

Important APIs and types: exports `s5p_mfc_wait_for_done_ctx`, `s5p_mfc_wait_for_done_dev`, `s5p_mfc_clean_ctx_int_flags`, and `s5p_mfc_clean_dev_int_flags`. It includes `s5p_mfc_common.h` so context and device structures are available.

Control flow: command issuers include this header, clear interrupt flags, issue a hardware/firmware command, then call the appropriate wait helper for the expected return command.

State and persistence: the header has no storage. Declared helpers mutate only transient `int_*` fields on MFC device/context structures.

Dependencies and integration points: integrates command, operation, stream, and control paths with the MFC interrupt handler through common interrupt state and wait queues.

Risks: the API returns only success or generic failure, so richer error handling requires inspecting other context/device fields. The `interrupt` boolean on the context wait is easy to misuse because it changes signal handling.

Test signals: compile coverage from all MFC command paths; runtime command-completion tests; and static checks that callers clean flags before waiting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_intr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_iommu.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_iommu.h

Purpose: provides a tiny Exynos IOMMU availability helper for the MFC driver.

Important APIs and types: defines inline `exynos_is_iommu_available(struct device *dev)`. With `CONFIG_EXYNOS_IOMMU`, it includes `<linux/iommu.h>` and returns whether `dev_iommu_priv_get(dev)` is non-NULL. Without that config, it always returns false.

Control flow: MFC setup code can call this helper to choose IOMMU-aware memory behavior without scattering Kconfig conditionals through implementation files.

State and persistence: no local state. It observes device IOMMU private data configured by the kernel IOMMU subsystem.

Dependencies and integration points: depends on `struct device`, `dev_iommu_priv_get`, and the `CONFIG_EXYNOS_IOMMU` build option. It integrates platform-specific Exynos IOMMU discovery with common MFC allocation and DMA setup paths.

Risks: availability is inferred from private data presence, not from successful domain attachment or runtime DMA mapping behavior. Non-Exynos builds always see false even if a generic IOMMU exists.

Test signals: build with and without `CONFIG_EXYNOS_IOMMU`; boot on Exynos platforms with IOMMU enabled and disabled; and DMA mapping tests confirming the selected memory path is valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr.c

Purpose: implements version selection for MFC hardware operations and shared private/generic DMA buffer allocation helpers.

Important APIs and functions: `s5p_mfc_init_hw_ops` selects v5 or v6+ `struct s5p_mfc_hw_ops` and sets the warning-code base. `s5p_mfc_init_regs` initializes register pointer tables for v6+ hardware. `s5p_mfc_alloc_priv_buf` and `s5p_mfc_release_priv_buf` allocate/free firmware-private buffers either from a pre-reserved bitmap-backed memory region or via coherent DMA allocation. `s5p_mfc_alloc_generic_buf` and `s5p_mfc_release_generic_buf` always use coherent DMA allocation.

Control flow: probe or device initialization calls `s5p_mfc_init_hw_ops` and then v6+ register setup. Codec operation backends call allocation helpers for instance buffers, context buffers, scratch buffers, and codec-private memory. Reserved-memory allocation searches `dev->mem_bitmap` for 64 KiB-aligned zero areas, records virtual and DMA addresses relative to `dev->mem_base`, and clears the bitmap on release. DMA allocation records the memory context and validates that the returned address is not below the configured base.

State and persistence: persistent driver-lifetime state includes `dev->mfc_ops`, `dev->mfc_regs`, `dev->warn_start`, the reserved-memory bitmap, and `struct s5p_mfc_priv_buf` fields (`ctx`, `virt`, `dma`, `size`). Buffer contents are zeroed by callers where required, not by these generic helpers.

Dependencies and integration points: depends on v5/v6 operation providers, MFC variant version macros, bitmap allocation, coherent DMA APIs, and per-bank memory devices/base addresses. It is the shared memory-management layer used by both decoder and encoder operation backends.

Risks: reserved-memory release assumes `b->dma` belongs to the reserved range and `b->size` is page-aligned. The bitmap allocation check uses `start > bits`; exact-end edge behavior depends on `bitmap_find_next_zero_area` semantics. DMA allocations below the configured base are rejected, but generic allocations do not perform that base validation. Release helpers assume the buffer was allocated and still has a valid size/context.

Test signals: boot/probe tests for v5 and v6+ variants; allocation failure injection; reserved-memory and IOMMU/coherent-DMA memory modes; repeated open/close to verify bitmap reuse; and DMA address sanity checks on platforms with multiple MFC memory banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr.h

Purpose: defines the version-independent MFC hardware operation interface and the register pointer map used by newer hardware backends.

Important APIs and types: `struct s5p_mfc_regs` contains `void __iomem *` pointers for common, decoder, and encoder registers across v6 through v12, including fields only present on selected versions. `struct s5p_mfc_hw_ops` is the driver-wide hardware abstraction, covering buffer allocation/release, DPB/source-size calculation, encoder stream/source buffer programming, scheduler `try_run`, interrupt flag clearing, decoder/encoder status getters, error decoding, crop/picture metadata getters, and scratch-size getters. Exported functions initialize ops/registers and allocate/release private or generic buffers.

Control flow: core code calls `s5p_mfc_init_hw_ops` and then invokes hardware methods with `s5p_mfc_hw_call`. Version-specific files fill this table with v5 or v6+ implementations. v6+ code also fills `struct s5p_mfc_regs` so later code can use symbolic pointer fields rather than raw offsets.

State and persistence: the header declares structure layouts only. Runtime state lives in `dev->mfc_ops`, `dev->mfc_regs`, and allocation buffers owned by `struct s5p_mfc_dev` or `struct s5p_mfc_ctx`.

Dependencies and integration points: includes `s5p_mfc_common.h` and is included by command, encoder, decoder, power/scheduler, and version-specific operation files. It is the primary interface between generic V4L2/context code and SoC-version register programming.

Risks: operation-table evolution is high risk because every version backend must populate compatible callbacks. `struct s5p_mfc_regs` contains many version-conditional fields, so callers must avoid using uninitialized fields on unsupported hardware. The interface mixes encoder, decoder, buffer-management, and status access, which makes regressions broad when signatures change.

Test signals: compile coverage for all supported MFC variants; static checks for initialized operation fields; runtime encode/decode on v5, v6/v7/v8, v10, and v12 devices; and fault-injection around allocation/release helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v5.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v5.c

Purpose: implements the hardware operation table for first-generation MFC v5 hardware, using bank-relative register offsets and a firmware shared-memory block.

Important APIs and functions: public entry is `s5p_mfc_init_hw_ops_v5`. Major local groups allocate/release decode descriptor, codec, instance, and shared buffers; calculate decoder DPB and encoder source sizes; program decode and encode stream/frame/reference buffers; write/read shared-memory offsets; configure common and codec-specific encoder parameters; issue decode/encode commands; run scheduler states in `s5p_mfc_try_run_v5`; clear interrupts; and expose status/error getters.

Control flow: v5 scheduling starts in `s5p_mfc_try_run_v5`, which refuses suspend, locks hardware, chooses a ready context, enables the MFC clock, clears context interrupt flags, then dispatches by decoder/encoder type and context state. Decoder states open/close instances, parse headers, initialize DPB buffers, decode frames, send last-frame commands, and handle resolution changes. Encoder states open/close instances, initialize sequence headers, program reference buffers, and encode frames or null final frames. Commands are issued by writing v5 `S5P_FIMV_*` registers directly, especially `S5P_FIMV_SI_CH0_INST_ID`.

State and persistence: per-context private buffers include descriptor (`dsc`), instance context (`ctx`), shared memory (`shm`), and codec banks (`bank1`, `bank2`). Shared memory stores firmware-visible fields such as crop info, frame tags, P/B QP, extended encoder control, frame rate timing, and VBV changes. v5 maintains separate left/right memory banks and uses `OFFSETA`/`OFFSETB` to convert DMA addresses to firmware offsets. Hardware state persists in registers until overwritten or reset.

Dependencies and integration points: depends on MFC command ops, interrupt helpers, power clock gating, v5 register definitions from common headers, vb2 DMA-contig addresses, coherent/private buffer allocation from `s5p_mfc_opr.c`, and V4L2 control values stored in `ctx->enc_params`. It is selected for non-v6-plus variants by `s5p_mfc_init_hw_ops`.

Risks: address arithmetic depends on correct per-bank DMA bases and `MFC_OFFSET_SHIFT`; wrong bank placement will program invalid hardware offsets. Shared-memory writes use raw typed pointer casts with memory barriers, so structure size/alignment assumptions are implicit. There is a suspicious stray closing brace after `s5p_mfc_run_res_change`, which would be a compile-time issue in this snapshot unless hidden by context. Many failure paths convert scheduling misses to `-EAGAIN`, making diagnostics dependent on logs. v5 does not report encoder DPB count and returns `-1` for some unsupported getters.

Test signals: v5 kernel build is mandatory; open/close instance smoke tests; H.264/MPEG4/H.263 encode and decode on v5 hardware; DPB allocation sizing under multiple resolutions; EOS/null-frame tests; resolution-change decode tests; and register trace comparison against known-good firmware command sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v5.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v5.h

Purpose: declares v5 operation-table initialization and defines v5 firmware shared-memory offsets.

Important APIs and types: `enum MFC_SHM_OFS` lists offsets for decode status, frame tags, timestamps, crop info, encoder extended control, parameter-change fields, metadata, allocated DPB sizes, VOP timing, HEC period, batch addresses, aspect ratio fields, debug history, hierarchical QP, and frame-packing SEI. The header exports `s5p_mfc_init_hw_ops_v5`.

Control flow: v5 operation code uses these offsets with `s5p_mfc_write_info_v5` and `s5p_mfc_read_info_v5` to exchange sideband information with firmware in the per-context shared-memory buffer.

State and persistence: no header-owned state. The enum defines the layout of `ctx->shm`, whose contents are volatile firmware/driver command state.

Dependencies and integration points: includes MFC common and operation headers. It tightly couples the v5 backend to firmware shared-memory ABI values; generic code sees only the returned `struct s5p_mfc_hw_ops`.

Risks: misspelled enum names such as `EXTENEDED_DECODE_STATUS` are ABI-neutral but easy to misuse. Any offset drift from firmware expectations breaks codec behavior. The include guard closing comment names `S5P_MFC_OPR_H_`, which is inconsistent but not functional.

Test signals: v5 build coverage; firmware command tests validating crop, QP, frame-rate, metadata, and frame-packing fields; and shared-memory dump checks during encode/decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v6.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v6.c

Purpose: implements the hardware operation table and register mapping for MFC v6 and later, including v7/v8/v10/v12 variations and newer codec support.

Important APIs and functions: public entries are `s5p_mfc_init_hw_ops_v6` and `s5p_mfc_init_regs_v6_plus`. Major functions allocate/release codec, instance, and device context buffers; calculate decoder DPB/source plane sizes; program decode/encode stream and frame buffers; set encoder reference, scratch, TMV, and ME buffers; configure generic encoder parameters and codec-specific H.264, MPEG4, H.263, VP8, and HEVC parameters; issue decode/encode commands; run the scheduler; clear interrupts; read status/error/crop/picture metadata; and map raw register offsets into `struct s5p_mfc_regs`.

Control flow: v6+ scheduling in `s5p_mfc_try_run_v6` locks hardware, selects a ready context, enables the clock, clears context interrupt flags, and dispatches by context type/state. Decoder states open/close instances, parse headers, initialize DPB buffers, flush, handle resolution changes, and decode normal or final frames via `cmd_host2risc`. Encoder states open/close instances, produce sequence headers, allocate/program reference buffers after header production, encode frames, send last-frame commands, or abort NALs. Register programming uses full DMA addresses rather than v5 bank offsets and writes through `dev->mfc_regs`.

State and persistence: per-context state includes instance buffers, codec bank buffers, scratch size, MV buffers, luma/chroma DPB sizes, ME/TMV buffer sizes, source strides, pixel format, and encoder parameter structures. Per-device state includes `ctx_buf`, static `mfc_regs`, firmware version, and current hardware context. The static `mfc_regs` object is overwritten on each `s5p_mfc_init_regs_v6_plus` call, so it is effectively global to the driver instance in this compilation unit.

Dependencies and integration points: depends on MFC command ops, interrupt helpers, clock gating, V4L2 pixel/control IDs, vb2 DMA-contig addresses, coherent/private buffer allocation, and version macros such as `IS_MFCV7_PLUS`, `IS_MFCV8_PLUS`, `IS_MFCV10_PLUS`, and `IS_MFCV12`. It is the backend selected for all v6+ variants by `s5p_mfc_init_hw_ops`.

Risks: register pointer initialization is version-sensitive and easy to regress when fields move between v6/v7/v8/v10/v12. Static `mfc_regs` can be problematic if multiple MFC devices with different bases or variants are active. Buffer size formulas vary heavily by codec, bit depth, chroma mode, and hardware version; underestimation causes firmware memory corruption or command failure. `s5p_mfc_release_codec_buffers_v6` assumes `bank1` was coherently allocated. HEVC control mapping has many bitfields and little local validation beyond V4L2 ranges. Like v5, scheduling failures unlock hardware and clock off without richer error propagation.

Test signals: allmodconfig/build coverage for all supported version macros; hardware encode/decode on v6/v7/v8/v10/v12; VP8 and HEVC coverage where supported; multi-plane YUV420/YVU420 and NV12/NV21 format tests; buffer-size stress at UHD and small odd dimensions; multi-device probe tests if hardware permits; register dumps compared to reference programming; and timeout/error-path tests around `cmd_host2risc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v6.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v6.h

Purpose: declares v6+ hardware operation/register initialization and defines shared v6+ sizing and encoder limit macros.

Important APIs and types: exports `s5p_mfc_init_hw_ops_v6` and `s5p_mfc_init_regs_v6_plus`. Defines macroblock and LCU dimension helpers, H.264/HEVC motion-vector buffer size formulas, encoder multi-slice, intra-refresh, VBV, loop-filter, frame-rate, profile/level, CBR, HEVC QP, and frame-delta limits.

Control flow: the v6+ operation implementation uses these macros when computing DPB, scratch, motion-estimation, and codec parameter limits. Generic initialization calls the exported functions to install the v6+ operation table and register pointer map.

State and persistence: no state is stored here. Macros influence runtime fields such as buffer sizes, QP ranges, and version-specific register programming.

Dependencies and integration points: includes common and operation headers, uses kernel `DIV_ROUND_UP`, and defines the v6+ backend boundary consumed by `s5p_mfc_opr.c`.

Risks: formulas and limit constants must stay aligned with firmware requirements. Changing them can silently affect memory allocation and V4L2 control range behavior. Some macros use broad integer expressions and depend on caller-provided dimensions being validated elsewhere.

Test signals: compile coverage; unit-style checks of buffer-size formulas if available; hardware stress at maximum resolutions and levels; and encode-control range tests for H.264 and HEVC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_opr_v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_pm.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_pm.c

Purpose: implements runtime power-management and clock-control helpers for the S5P MFC device.

Important APIs and functions: `s5p_mfc_init_pm` acquires variant clocks and enables runtime PM. `s5p_mfc_final_pm` disables runtime PM. `s5p_mfc_clock_on`/`s5p_mfc_clock_off` gate the selected software clock gate. `s5p_mfc_power_on` resumes the device and prepares/enables all clocks. `s5p_mfc_power_off` re-enables the gate clock, disables/unprepares all clocks, and drops the runtime PM reference.

Control flow: probe initializes `dev->pm` from variant clock names and device pointers, treating missing additional clocks as optional. Power-on resumes runtime PM, enables clocks in order, and rolls back already enabled clocks on failure. After enabling, it disables `clock_gate` so scheduler paths can explicitly enable/disable it around hardware operations. Power-off reverses this by enabling `clock_gate` before disabling all prepared clocks.

State and persistence: `dev->pm` stores clock count, names, clock pointers, runtime PM device, and optional `clock_gate`. Clock and PM state persists while the device is bound and changes during hardware scheduling, suspend/resume, and stream operations.

Dependencies and integration points: depends on Linux common clock framework, runtime PM, platform device state, and MFC variant data. Operation backends call `s5p_mfc_clock_on/off` around firmware work; probe/remove and system PM paths call power helpers.

Risks: `s5p_mfc_clock_on/off` call `clk_enable/disable` on `clock_gate`; if `use_clock_gating` is false and `clock_gate` remains NULL, callers must not use these helpers or clock APIs must tolerate the pointer. Optional-clock handling only ignores `-ENOENT` for nonzero clock indexes. Failure rollback in `power_on` assumes only clocks before index `i` were enabled.

Test signals: probe/remove with variants having one clock, multiple clocks, and optional missing clocks; runtime suspend/resume; stream start/stop clock balance; failure injection for `clk_prepare_enable`; and lockdep/PM-runtime warnings under concurrent contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_pm.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_pm.h

Purpose: declares MFC runtime PM, power, and clock helper functions.

Important APIs and types: exports `s5p_mfc_init_pm`, `s5p_mfc_final_pm`, `s5p_mfc_clock_on`, `s5p_mfc_clock_off`, `s5p_mfc_power_on`, and `s5p_mfc_power_off`, all operating on `struct s5p_mfc_dev`.

Control flow: device probe initializes PM, runtime stream/scheduler paths gate clocks, and remove or failure paths finalize PM and power down resources.

State and persistence: no state is held in the header. Declared functions mutate `dev->pm`, runtime PM usage count, and clock prepare/enable state.

Dependencies and integration points: requires consumer visibility of `struct s5p_mfc_dev`. It is included by operation backends and core device setup code.

Risks: the API separates whole-device power from software clock gating, so callers must pair the correct helper families. Misbalanced calls can leave firmware inaccessible or clocks enabled.

Test signals: compile coverage; runtime PM balance checks; stream start/stop cycles; and suspend/resume tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/Kconfig

Purpose: introduces the STMicroelectronics media platform driver submenu and sources the ST platform Kconfig fragments.

Important APIs and symbols: emits a Kconfig `comment` and sources `drivers/media/platform/st/sti/Kconfig` plus `drivers/media/platform/st/stm32/Kconfig`.

Control flow: when the media platform Kconfig tree is evaluated, this file delegates actual driver symbols to the STI and STM32 subtrees.

State and persistence: no runtime state. Selected symbols persist only in kernel configuration.

Dependencies and integration points: integrates the ST platform directory with the wider Linux media Kconfig hierarchy.

Risks: incorrect source paths would hide all ST platform driver options. The file itself defines no guards or dependencies, so subtrees must own symbol constraints.

Test signals: `menuconfig` visibility under media platform drivers and allmodconfig/allnoconfig parse coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/Makefile

Purpose: includes ST media platform child directories in kbuild.

Important APIs and entries: unconditionally adds `sti/bdisp/`, `sti/delta/`, `sti/hva/`, and `stm32/` to `obj-y`.

Control flow: kbuild descends into these directories, where child Makefiles decide actual objects based on Kconfig symbols.

State and persistence: no runtime state. It controls build traversal only.

Dependencies and integration points: links the top-level ST media platform directory to STI and STM32 media drivers.

Risks: unconditional descent is normal but requires each child directory to be build-safe when its symbols are disabled. Missing a new child directory here would prevent its Makefile from being evaluated.

Test signals: kbuild traversal in disabled and enabled configurations; allmodconfig; and `make M=drivers/media/platform/st`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/Kconfig

Purpose: sources Kconfig fragments for STI-generation ST media drivers.

Important APIs and symbols: sources `bdisp/Kconfig`, `delta/Kconfig`, and `hva/Kconfig`.

Control flow: selecting the ST platform Kconfig subtree causes these three driver configuration files to be parsed in order.

State and persistence: no runtime state. Kconfig selections persist in the kernel `.config`.

Dependencies and integration points: connects STI BDISP, DELTA, and HVA media drivers to the ST Kconfig tree.

Risks: path mismatches hide driver options. Since this file defines no common dependency, each child Kconfig must enforce architecture, media framework, and compile-test constraints.

Test signals: Kconfig parse tests and menu visibility for BDISP, DELTA, and HVA symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/Makefile

Purpose: descends into STI media driver build directories.

Important APIs and entries: unconditionally adds `bdisp/`, `delta/`, `hva/`, and `stm32/` to `obj-y`.

Control flow: kbuild evaluates child Makefiles, which conditionally build objects based on their Kconfig symbols.

State and persistence: no runtime state. Build traversal is the only effect.

Dependencies and integration points: integrates STI media subdrivers with kbuild. The `stm32/` child entry is notable because STM32 is also referenced from the parent ST Makefile, so tree layout should be checked in the full source context.

Risks: adding `stm32/` under `sti/` can fail if that relative directory does not exist in this source tree, depending on kbuild traversal behavior. Unconditional descent requires children to be disabled-clean.

Test signals: `make M=drivers/media/platform/st/sti` and full media builds with all ST drivers disabled and enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/Kconfig

Purpose: defines the Kconfig symbol for the STMicroelectronics BDISP 2D blitter V4L2 mem2mem driver.

Important APIs and symbols: `VIDEO_STI_BDISP` is a tristate depending on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and `ARCH_STI || COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG` and `V4L2_MEM2MEM_DEV`.

Control flow: enabling this symbol causes the BDISP Makefile to build the BDISP module/object from V4L2, hardware, and debug components.

State and persistence: no runtime state. The symbol persists in kernel configuration and determines module availability.

Dependencies and integration points: integrates BDISP with the V4L2 mem2mem framework, video device core, and contiguous videobuf2 DMA allocator on STi SoCs or compile-test builds.

Risks: missing dependencies for clocks, reset, runtime PM, or debugfs would surface only at build/link time if used by implementation files. Compile-test support increases coverage but may expose architecture assumptions.

Test signals: Kconfig visibility, allmodconfig, COMPILE_TEST builds, and runtime module load on ARCH_STI platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/Makefile

Purpose: maps the BDISP Kconfig symbol to its composite driver object.

Important APIs and entries: `obj-$(CONFIG_VIDEO_STI_BDISP) += bdisp.o` and `bdisp-objs := bdisp-v4l2.o bdisp-hw.o bdisp-debug.o`.

Control flow: when `VIDEO_STI_BDISP` is enabled, kbuild links V4L2 frontend, hardware programming, and debugfs/performance support into one BDISP driver object or module.

State and persistence: no runtime state. It determines build composition.

Dependencies and integration points: depends on the Kconfig symbol defined in the same directory and on the listed implementation files.

Risks: adding new implementation files requires updating `bdisp-objs`. Removing debug support would require handling references from the V4L2/hardware files.

Test signals: enabled/disabled module builds and link checks for all BDISP objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-debug.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-debug.c

Purpose: implements debugfs and performance diagnostic support for the ST BDISP 2D blitter driver.

Important APIs and functions: exported driver-facing helpers are `bdisp_dbg_perf_begin`, `bdisp_dbg_perf_end`, `bdisp_debugfs_create`, and `bdisp_debugfs_remove`. Debugfs show callbacks include `regs_show`, `last_nodes_show`, `last_nodes_raw_show`, `last_request_show`, and `perf_show`. Numerous dump helpers decode BDISP node fields such as instruction bits, target/source pixel types, coordinates, sizes, filter control, resize factors, resize initial values, and color-conversion matrices.

Control flow: hardware request paths call `bdisp_dbg_perf_begin` before processing and `bdisp_dbg_perf_end` after completion to update last/min/max/total duration. Probe/debug setup calls `bdisp_debugfs_create`, which creates a per-device directory named from `BDISP_NAME` and `bdisp->id`, then installs read-only debugfs files. Reading `regs` resumes the device with runtime PM, dumps static, plug, node, filter, and luma-filter registers, then releases PM. Reading `last_nodes` decodes copied nodes until `MAX_NB_NODE` or a zero next-node pointer; `last_nodes_raw` dumps raw node words; `last_request` summarizes copied source/destination request geometry; `perf` reports average/min/max/last processing time and approximate FPS.

State and persistence: diagnostic state lives under `bdisp->dbg`, including copied node pointers, copied request, debugfs dentry, hardware start time, and performance duration counters. This is volatile runtime/debug state and is reset when the device is removed or driver state is reinitialized. Debugfs files expose current in-memory snapshots only.

Dependencies and integration points: depends on Linux debugfs, seq_file show helpers, runtime PM, BDISP core structures from `bdisp.h`, coefficient constants from `bdisp-filter.h`, and register/bit definitions from `bdisp-reg.h`. It integrates with the main BDISP driver through copied request/node snapshots and performance hooks.

Risks: debugfs has no stable ABI, but it can still expose stale copied pointers if lifecycle handling outside this file is wrong. `regs_show` wakes hardware for register reads and could perturb power-management timing. FPS math divides by duration fields; `min_duration` is initialized on first request, but corrupted or zero state could divide by zero. Raw node dumps expose DMA programmed values, which may be sensitive in debug environments. Directory name uses a fixed 16-byte buffer and depends on `BDISP_NAME` plus id fitting.

Test signals: build with `CONFIG_DEBUG_FS`; probe creates expected debugfs files; reading each file before and after a request; runtime PM balance after `regs`; performance counters across multiple requests; and lockdep/KASAN tests for remove while debugfs readers are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-filter.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-filter.h

Purpose: defines BDISP filter coefficient structure shapes and standard RGB/YUV conversion matrix constants.

Important APIs and types: `BDISP_HF_NB` and `BDISP_VF_NB` define horizontal and vertical coefficient counts. `struct bdisp_filter_h_spec` and `struct bdisp_filter_v_spec` store fixed-point scale factor min/max values and coefficient arrays. Static arrays `bdisp_rgb_to_yuv` and `bdisp_yuv_to_rgb` hold four 32-bit matrix words for BT.601-style conversion.

Control flow: hardware programming and debug code include this header to describe filter tables and to recognize or program standard color-conversion matrices. `bdisp-debug.c` compares IVXM register values against these arrays to print RGB-to-YUV or YUV-to-RGB labels.

State and persistence: the header defines static const data per translation unit that includes it. There is no mutable state.

Dependencies and integration points: depends on kernel integer typedefs such as `u8`, `u16`, and `u32` supplied by including files. Integrates BDISP scaling/filter code and debug interpretation with the same coefficient and matrix definitions.

Risks: the header has no include guard, so multiple inclusion in one translation unit would redefine structs and static arrays. Static const arrays in a header create a private copy per including C file. Matrix values must match hardware register encoding and colorimetry expectations.

Test signals: compile coverage for all includers; scaling tests that select expected coefficient specs; debugfs IVXM decoding for known conversion matrices; and visual/color validation for RGB/YUV blits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/bdisp/bdisp-filter.h -->
