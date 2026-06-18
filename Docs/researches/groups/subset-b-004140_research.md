# subset-b-004140 research

Grouped research for MediaTek JPEG, legacy MDP, and MDP3 driver files. Each section preserves the original source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_hw.c

## Purpose
This file implements the MediaTek JPEG decoder hardware helper layer and the per-hardware-block platform driver for MT8195 JPEG decode engines. It converts parsed JPEG frame parameters into hardware register programming, handles decoder interrupts/timeouts, returns V4L2 mem2mem buffers, and registers child decode engines with the master JPEG core.

## Important APIs, Types, and Functions
The exported decoder programming APIs are `mtk_jpeg_dec_fill_param()`, `mtk_jpeg_dec_get_int_status()`, `mtk_jpeg_dec_enum_result()`, `mtk_jpeg_dec_set_config()`, `mtk_jpeg_dec_reset()`, and `mtk_jpeg_dec_start()`. Internal helpers classify JPEG sampling patterns, calculate MCU counts, DMA grouping, component strides and payload sizes, and write decoder registers for bitstream addresses, destination banks, component IDs, sampling factors, quantization table IDs, and 34-bit address extensions. Platform-driver entry points are `mtk_jpegdec_hw_probe()` and `mtk_jpegdec_hw_irq_handler()`.

## Control Flow
The parser or core fills `struct mtk_jpeg_dec_param`, then `mtk_jpeg_dec_fill_param()` derives output fourcc, MCU layout, DMA group sizing, strides, and component byte sizes. For a job, the core supplies bitstream and framebuffer DMA addresses to `mtk_jpeg_dec_set_config()`, which programs the decoder in a fixed order before `mtk_jpeg_dec_start()` triggers hardware. The IRQ handler cancels timeout work, copies source metadata to the destination, reads and clears interrupt status, resets on underflow/overflow/bitstream errors, sets destination plane payloads from computed component sizes, returns buffers, drops runtime PM and the decode clock, marks the hardware idle, and wakes the master scheduler.

## State and Persistence
Hardware state is volatile MMIO register state. Software state is held in the child `struct mtk_jpegdec_comp_dev`, including `hw_param`, `hw_state`, register base, clocks, IRQ, and delayed timeout work. Destination completion order is persisted only in the V4L2 context done queue through frame numbers and `last_done_frame_num`; it is not durable across device reset or stream teardown.

## Dependencies and Integration Points
The file depends on V4L2 mem2mem/videobuf2 buffer lifetimes, `mtk_jpeg_core.h` context and child-device structures, register offsets from `mtk_jpeg_dec_reg.h`, runtime PM, clock bulk APIs, platform IRQ/MMIO helpers, and OF compatible `mediatek,mt8195-jpgdec-hw`. It integrates with the master JPEG device through `master_dev->dec_hw_dev`, `reg_decbase`, `hw_index`, `hw_rdy`, and `hw_wq`.

## Risks and Edge Cases
Sampling recognition is strict; unsupported sampling combinations produce `dst_fourcc = 0` and fail parameter fill. Address and size alignment failures only log through `mtk_jpeg_verify_align()`; callers do not get a hard failure during register programming. Several register fields subtract one from calculated counts, so zero MCU, group, or unit counts would underflow if invalid dimensions reached this layer. `mtk_jpegdec_put_buf()` maintains ordered destination completion under a spinlock, so frame-number initialization and wrap behavior matter. Timeout and IRQ paths both manipulate PM, clocks, source buffers, and destination completion, making delayed-work cancellation and hardware state transitions important race signals.

## Test Signals
Useful tests include decode jobs for grayscale, 4:2:0, 4:2:2, vertical 4:2:2, 4:4:4, and MTK 34-bit DMA variants; invalid sampling tables; unaligned bitstream/output DMA addresses; underflow/overflow/error IRQ injection; timeout recovery; multi-hardware scheduling; and V4L2 plane payload checks against `comp_size[]`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_hw.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_hw.h

## Purpose
This header defines the MediaTek JPEG decoder hardware ABI used between the parser/core and the hardware programming file. It exposes decoder result codes, decoded-frame parameter storage, bitstream/framebuffer DMA descriptors, and register-control function prototypes.

## Important APIs, Types, and Functions
`struct mtk_jpeg_dec_param` is the central decoded-frame description: picture size, output size/fourcc, component IDs, sampling factors, quantization-table IDs, MCU and DMA grouping, membership map, strides, component sizes, and UV downscale state. `struct mtk_jpeg_bs` describes input bitstream DMA start/end/size. `struct mtk_jpeg_fb` describes destination plane DMA addresses. Public APIs include fill, interrupt classification, reset/start, and full hardware configuration.

## Control Flow
JPEG marker parsing fills the raw SOF-derived fields, then `mtk_jpeg_dec_fill_param()` populates derived fields before `mtk_jpeg_dec_set_config()` consumes the same structure to program hardware. Interrupt handlers use the result enum returned by `mtk_jpeg_dec_enum_result()`.

## State and Persistence
The header defines in-memory job state only. The structures are per decode operation or per queued buffer and are not persistent storage. Their correctness controls hardware register state and V4L2 payload reporting.

## Dependencies and Integration Points
It includes videobuf2 core types and `mtk_jpeg_dec_reg.h`, and it is shared by parser, core scheduling code, and decode hardware implementation. `MTK_JPEG_COMP_MAX` fixes the decoder model to at most three JPEG components.

## Risks and Edge Cases
The structures do not encode validity ranges, so callers must prevent invalid component counts, zero dimensions, unsupported sampling factors, and insufficient destination planes. `size_t` and `dma_addr_t` fields are architecture-dependent and must match the register programming paths, especially with 34-bit address support.

## Test Signals
Compile coverage should catch prototype drift. Runtime tests should confirm all fields are filled before hardware programming, plane arrays are bounded by `MTK_JPEG_COMP_MAX`, and result-code mapping matches documented interrupt bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_parse.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_parse.c

## Purpose
This file parses enough of a JPEG bitstream to extract baseline SOF0 image properties needed by the MediaTek JPEG decoder hardware. It reads dimensions, component count, component IDs, sampling factors, and quantization table selectors, then asks the hardware helper to derive decoder configuration.

## Important APIs, Types, and Functions
`struct mtk_jpeg_stream` is a small bounds-checked cursor over the mapped source buffer. `read_byte()`, `read_word_be()`, and `read_skip()` implement marker walking. `mtk_jpeg_do_parse()` scans markers and fills `struct mtk_jpeg_dec_param`. `mtk_jpeg_parse()` is the exported parser entry that also calls `mtk_jpeg_dec_fill_param()`.

## Control Flow
The parser scans until it sees marker prefix `0xff`, skips fill bytes, ignores stuffed zero bytes, and switches on the marker code. SOI, EOI, TEM, and restart markers have no length payload. Unknown/unused markers are skipped using their big-endian length. On SOF0 it reads precision, height, width, component count, and per-component ID/sampling/quant table fields; success requires one or three complete components. It returns false if the stream ends or derived hardware parameters are unsupported.

## State and Persistence
All parser state is stack-local except for fields written into the caller-provided `struct mtk_jpeg_dec_param`. There is no persistence beyond the decode job.

## Dependencies and Integration Points
The parser depends on Linux media JPEG marker constants from `<media/jpeg.h>`, V4L2 types, and `mtk_jpeg_dec_fill_param()` from the hardware helper. It integrates with the JPEG core before queueing/configuring a decode job.

## Risks and Edge Cases
Only SOF0 baseline frames are accepted; progressive or other SOF markers are not parsed. `read_skip()` repeatedly consumes bytes and ignores short-skip failure, so a truncated non-SOF segment only fails on a later read. Component arrays rely on `comp_num` being one or three. The code uses `int` for byte reads and stores into unsigned fields, making `-1` checks critical before assignment.

## Test Signals
Feed valid baseline grayscale and YUV JPEG headers, progressive JPEGs, truncated headers, marker stuffing/fill-byte sequences, restart markers before SOF0, invalid component counts, and unsupported sampling factors. Expected signals are boolean parse results and correctly derived decoder formats/strides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_parse.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_parse.h

## Purpose
This header exposes the JPEG decode parser entry point to the MediaTek JPEG core.

## Important APIs, Types, and Functions
It forward-declares `struct mtk_jpeg_dec_param` through the included hardware header and declares `bool mtk_jpeg_parse(struct mtk_jpeg_dec_param *param, u8 *src_addr_va, u32 src_size)`.

## Control Flow
Callers pass a virtually mapped source buffer and its size. On success the provided decode parameter structure contains both parsed JPEG metadata and derived hardware layout.

## State and Persistence
No state is stored by the header. The caller owns the parameter object and source buffer lifetime.

## Dependencies and Integration Points
It includes `mtk_jpeg_dec_hw.h` because parsing is tied directly to decoder hardware parameter derivation. It is the bridge between bitstream parsing code and V4L2 decode scheduling.

## Risks and Edge Cases
The API does not expose detailed parse errors, so users only learn success or failure. Callers must ensure the source virtual address is valid for `src_size` bytes and remains mapped during parsing.

## Test Signals
Compile checks should verify the parser declaration stays in sync. Runtime decode setup should reject invalid JPEG headers by observing a false return from this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_reg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_reg.h

## Purpose
This header is the decoder register map for the MediaTek JPEG decode block. It names MMIO offsets, interrupt-status bits, and hardware constants consumed by `mtk_jpeg_dec_hw.c`.

## Important APIs, Types, and Functions
The file exports macros rather than functions. Important constants include `MTK_JPEG_BLOCK_MAX`, `MTK_JPEG_DCTSIZE`, interrupt masks such as `BIT_INQST_MASK_EOF` and `BIT_INQST_MASK_ALLIRQ`, base decoder control registers such as `JPGDEC_REG_RESET`, bitstream registers such as `JPGDEC_REG_FILE_ADDR`, output registers such as `JPGDEC_REG_DEST_ADDR0_Y`, and 34-bit extension registers.

## Control Flow
There is no executable control flow. The hardware helper composes register writes using these offsets during reset, configuration, trigger, and interrupt handling.

## State and Persistence
The macros describe volatile hardware state. Persistence is in the hardware register file only while the block is powered and configured.

## Dependencies and Integration Points
The header is included by `mtk_jpeg_dec_hw.h` and indirectly by parser/core users. The offsets must match the MediaTek JPEG decoder IP revision selected by device-tree compatibles.

## Risks and Edge Cases
Incorrect offsets or masks can corrupt unrelated decoder registers. The interrupt mask includes EOF, pause, underflow, overflow, and bitstream error but not every possible status bit, so new hardware status bits would need explicit handling. Extension-register use must stay aligned with platform 34-bit support.

## Test Signals
Register trace comparison against hardware documentation, IRQ status injection, and decode smoke tests on MT8195 are the main validation signals. Build tests catch only macro spelling, not semantic drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_dec_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_enc_hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_enc_hw.c

## Purpose
This file implements MediaTek JPEG encoder hardware programming and the MT8195 JPEG encode hardware child platform driver. It writes source/destination DMA addresses, image size, stride, quality, restart interval, EXIF offset behavior, handles encoder completion/timeout, and registers encoder engines with the master JPEG device.

## Important APIs, Types, and Functions
Exported APIs are `mtk_jpeg_enc_reset()`, `mtk_jpeg_enc_get_file_size()`, `mtk_jpeg_enc_start()`, `mtk_jpeg_set_enc_src()`, `mtk_jpeg_set_enc_dst()`, and `mtk_jpeg_set_enc_params()`. `mtk_jpeg_enc_quality[]` maps user quality thresholds to hardware quality codes. Runtime platform hooks include `mtk_jpegenc_hw_probe()`, `mtk_jpegenc_hw_irq_handler()`, timeout work, IRQ setup, and ordered destination completion via `mtk_jpegenc_put_buf()`.

## Control Flow
For a job, the core sets source plane DMA addresses, destination DMA window and optional EXIF offset, encoder size/stride/block count/quality/control bits, then calls `mtk_jpeg_enc_start()`. The IRQ handler cancels timeout work, copies metadata, clears interrupt status, warns on non-DONE interrupts, calculates output byte count from DMA pointer registers, sets destination payload, returns source and destination buffers, releases runtime PM/clocks, marks the hardware idle, and wakes the master scheduler. Timeout work resets hardware and completes the source as error while still returning the destination through the ordered completion queue.

## State and Persistence
Per-engine runtime state lives in `struct mtk_jpegenc_comp_dev`: current buffers/context, delayed timeout work, register base, clocks, IRQ, and hardware state. Per-context encode controls such as quality, restart interval, output format, crop, and EXIF enable drive register state but are not persisted by this file.

## Dependencies and Integration Points
The code depends on videobuf2 DMA-contig addresses, V4L2 mem2mem buffer handling, runtime PM, MediaTek JPEG core structures, and OF compatible `mediatek,mt8195-jpgenc-hw`. It integrates with the master device through `enc_hw_dev`, `reg_encbase`, `hw_index`, `hw_rdy`, and `hw_wq`.

## Risks and Edge Cases
`mtk_jpeg_enc_get_file_size()` infers size by subtracting destination base from the current DMA pointer; 34-bit handling shifts `DMA_ADDR0` but does not combine all high bits in an obvious way. `mtk_jpeg_set_enc_dst()` writes `addr_ext + size` for the stall extension, which is suspicious if the extension register expects only high address bits. Format-dependent block count and stride logic must match supported V4L2 formats. Timeout and IRQ paths share buffer/clock/PM cleanup responsibilities, so cancellation ordering matters.

## Test Signals
Exercise NV12/NV21 and packed 4:2:2 formats, all quality thresholds, EXIF and non-EXIF output, restart intervals, 34-bit DMA addresses, output buffer near stall boundary, timeout recovery, non-DONE IRQ status, and ordered completion under multi-frame scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_enc_hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_enc_hw.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_enc_hw.h

## Purpose
This header defines JPEG encoder register offsets, control bits, quality codes, and exported hardware programming functions for the MediaTek JPEG encoder.

## Important APIs, Types, and Functions
Important macros include interrupt status bits, destination byte-offset mask, control bits for enable/interrupt/file-format/restart/YUV format, reset bit, hardware YUV format encodings, quality-code constants, and MMIO offsets from `JPEG_ENC_RSTB` through 34-bit address extension registers. `struct mtk_jpeg_enc_qlt` maps a public quality value to a hardware code. The exported functions reset, start, compute file size, and program source, destination, and encode parameters.

## Control Flow
The core includes this header to call the encoder setup sequence before starting hardware. The IRQ path also uses the file-size helper to set the captured JPEG payload.

## State and Persistence
The header has no runtime state. It defines the volatile register contract and the small immutable quality mapping element type.

## Dependencies and Integration Points
It includes videobuf2 core and `mtk_jpeg_core.h`, tying encoder programming to V4L2 buffer/context state. Register definitions are consumed only by the encoder implementation.

## Risks and Edge Cases
Macro drift from hardware documentation can silently break encoding. The `JEPG_ENC_YUV_FORMAT_NV21` spelling is typoed but still usable as a macro name if referenced. The register interface assumes callers provide correctly aligned DMA addresses and format-compatible context fields.

## Test Signals
Compile coverage, register trace checks, quality/format matrix encode tests, and 34-bit DMA tests validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/jpeg/mtk_jpeg_enc_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/Kconfig

## Purpose
This Kconfig entry exposes the legacy MediaTek MT8173 MDP V4L2 mem2mem driver.

## Important APIs, Types, and Functions
The key symbol is `VIDEO_MEDIATEK_MDP`, a tristate option that selects `VIDEOBUF2_DMA_CONTIG`, `V4L2_MEM2MEM_DEV`, and `VIDEO_MEDIATEK_VPU`. It depends on V4L mem2mem drivers, media video device support, MediaTek IOMMU/SMI conditions, and MediaTek architecture or compile-test builds.

## Control Flow
When enabled, Kbuild descends into the `mdp` Makefile and links `mtk-mdp.o`. Runtime control flow is implemented in the C files.

## State and Persistence
The selected value persists in the kernel `.config`, controlling whether the driver is built in, modular, or omitted.

## Dependencies and Integration Points
The symbol couples this driver to V4L2, vb2 DMA-contig, the MediaTek VPU firmware interface, IOMMU, and SMI. It is platform-specific to MT8173-era MDP.

## Risks and Edge Cases
Dependency relaxation for `COMPILE_TEST && MTK_SMI=n` must continue to cover non-MediaTek build testing without exposing impossible runtime configurations. Selecting VPU support means builds must keep the VPU include path and symbols available.

## Test Signals
Run `olddefconfig`, `allmodconfig`, MediaTek ARM64 builds, and compile-test builds with and without `MTK_SMI`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/Makefile

## Purpose
This Makefile builds the legacy MediaTek MDP driver object from its core, component, mem2mem, register/VPU-configuration, and VPU transport sources.

## Important APIs, Types, and Functions
`mtk-mdp-y` aggregates `mtk_mdp_core.o`, `mtk_mdp_comp.o`, `mtk_mdp_m2m.o`, `mtk_mdp_regs.o`, and `mtk_mdp_vpu.o`. `obj-$(CONFIG_VIDEO_MEDIATEK_MDP)` emits the final `mtk-mdp` module or built-in object. `ccflags-y` adds the MediaTek VPU include directory.

## Control Flow
Kbuild evaluates `CONFIG_VIDEO_MEDIATEK_MDP` and compiles the aggregate object list if enabled.

## State and Persistence
There is no runtime state. The Makefile persists build composition.

## Dependencies and Integration Points
It is coupled to `Kconfig`, local source filenames, and `drivers/media/platform/mediatek/vpu` headers.

## Risks and Edge Cases
Renaming any source file or moving VPU headers requires synchronized Makefile changes. Missing one object can produce link failures or a driver without a core subsystem.

## Test Signals
Targeted `make drivers/media/platform/mediatek/mdp/`, `allmodconfig`, and module load checks are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_comp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_comp.c

## Purpose
This file manages legacy MDP component discovery resources, specifically device-tree node references and clocks for RDMA, RSZ, WDMA, and WROT blocks.

## Important APIs, Types, and Functions
`mtk_mdp_comp_init()` records the component OF node, type, and clocks. `mtk_mdp_comp_deinit()` drops the node reference. `mtk_mdp_comp_clock_on()` and `mtk_mdp_comp_clock_off()` enable/disable all stored clocks, with RDMA allowed two clocks and other components stopping after the first clock.

## Control Flow
The core driver allocates a `struct mtk_mdp_comp` for each matched sibling/child node, calls init, links it into `mdp->comp_list`, then runtime PM suspend/resume or driver-wide clock helpers iterate the list to toggle clocks.

## State and Persistence
Component state is in `struct mtk_mdp_comp`: list node, retained OF node, up to two clock pointers, and component type. The state lasts for the platform device lifetime.

## Dependencies and Integration Points
The file depends on common clock APIs and OF node lookup. It is used by `mtk_mdp_core.c` for probe/remove and runtime PM.

## Risks and Edge Cases
Clock acquisition treats any missing clock as fatal, but only RDMA is expected to have two clocks. If device-tree clock ordering changes, RDMA secondary-clock behavior can break. Clock enable failures are logged but `mtk_mdp_comp_clock_on()` continues enabling remaining clocks and does not unwind already enabled clocks.

## Test Signals
Probe with old and new MT8173 device-tree layouts, missing clocks, disabled components, runtime suspend/resume, and repeated open/close cycles while checking balanced clock prepare counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_comp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_comp.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_comp.h

## Purpose
This header defines the legacy MDP component model and clock/resource helper prototypes.

## Important APIs, Types, and Functions
`enum mtk_mdp_comp_type` names RDMA, RSZ, WDMA, and WROT. `struct mtk_mdp_comp` stores a list node, OF node, two possible clocks, and type. The declared helpers initialize/deinitialize components and toggle component clocks.

## Control Flow
The core driver includes this header to build a component list during probe and to control clocks during PM transitions.

## State and Persistence
The header defines per-component in-memory state that persists for the driver binding lifetime.

## Dependencies and Integration Points
It is consumed by `mtk_mdp_core.c` and `mtk_mdp_comp.c`, and indirectly by the context/device definitions in `mtk_mdp_core.h`.

## Risks and Edge Cases
The fixed `clk[2]` array assumes no component needs more clocks. Adding new component types requires updating DT matching and any clock special cases.

## Test Signals
Compile coverage and runtime probe on DT nodes for every enum type validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_comp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_core.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_core.c

## Purpose
This is the legacy MediaTek MDP platform driver core. It discovers component blocks, registers the V4L2 mem2mem video device, obtains the VPU platform device, registers a VPU watchdog reset handler, and implements global runtime/system PM clock handling.

## Important APIs, Types, and Functions
Key functions are `mtk_mdp_probe()`, `mtk_mdp_remove()`, `mtk_mdp_register_component()`, `mtk_mdp_unregister_component()`, PM callbacks, and VPU watchdog work/reset handlers. It exports the debug-level module parameter `mtk_mdp_dbg_level`.

## Control Flow
Probe allocates `struct mtk_mdp_dev`, handles old child-node and newer sibling-node DT layouts, creates and registers component records, creates job and watchdog workqueues, registers the V4L2 device and mem2mem node, obtains the VPU device, registers VPU watchdog handling, sets vb2 DMA max segment size, and enables runtime PM. Remove reverses those resources. Runtime/system suspend disables all component clocks; resume enables them. A VPU watchdog callback queues work that marks every active context error.

## State and Persistence
Driver state persists in `struct mtk_mdp_dev`: locks, component list, context list, V4L2/m2m objects, workqueues, VPU device, counters, and watchdog work. Context error flags survive until each context is released or reset by higher layers.

## Dependencies and Integration Points
The core depends on platform/OF, common clocks through components, runtime PM, V4L2/vb2, the MediaTek VPU driver, and `mtk_mdp_m2m.c` registration. It binds `mediatek,mt8173-mdp` and component compatibles under the same parent.

## Risks and Edge Cases
Old/new DT layout support requires careful parent selection. Disabled components are skipped, which may leave the VPU firmware with missing hardware paths. Probe error unwinding must keep component OF references and workqueues balanced. VPU watchdog sets all contexts into error state but does not itself drain queued buffers. Runtime PM clock-on logs but does not fail resume on individual component clock errors.

## Test Signals
Probe/remove on both DT layouts, disabled component nodes, VPU firmware absence, VPU watchdog reset, runtime suspend/resume while streaming idle, and V4L2 device registration/unregistration are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_core.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_core.h

## Purpose
This header is the central data model for the legacy MediaTek MDP driver. It defines pixel format metadata, frames, controls, variant limits, the global device object, and per-file V4L2 mem2mem context.

## Important APIs, Types, and Functions
Important types include `struct mtk_mdp_fmt`, `struct mtk_mdp_frame`, `struct mtk_mdp_variant`, `struct mtk_mdp_dev`, and `struct mtk_mdp_ctx`. It defines format flags, VPU/context state bits, module name, shutdown timeout, and debug macros. It declares component registration helpers and exports `mtk_mdp_dbg_level`.

## Control Flow
Most source files include this header. The core populates `struct mtk_mdp_dev`; the mem2mem frontend allocates and configures `struct mtk_mdp_ctx`; register/VPU helper code consumes the context to fill shared VPU configuration.

## State and Persistence
`struct mtk_mdp_dev` stores driver-global runtime state for the platform binding. `struct mtk_mdp_ctx` stores per-open-file configuration, V4L2 controls, colorimetry, VPU instance state, and queued work. None of this is durable beyond module/device lifetime.

## Dependencies and Integration Points
The header integrates V4L2 controls, V4L2 device/mem2mem, videobuf2 DMA-contig, MediaTek VPU state, and MDP component definitions.

## Risks and Edge Cases
Many fields are shared across ioctl, queue, worker, watchdog, and release paths, so lock ownership matters. The header references `struct mtk_mdp_pix_limit` before its definition appears in `mtk_mdp_m2m.c`, so the pointer-only use is intentional. Debug macros compile out unless `DEBUG` is defined, which can hide diagnostics in production builds.

## Test Signals
Compile with and without `DEBUG`, run V4L2 format/control/streaming tests across multiple simultaneous contexts, and validate watchdog context-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_ipi.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_ipi.h

## Purpose
This header defines the packed AP-to-VPU IPI message ABI and shared MDP process configuration for the legacy driver.

## Important APIs, Types, and Functions
Message IDs cover AP init/deinit/process and VPU acknowledgements. `struct mdp_ipi_init`, `struct mdp_ipi_comm`, and `struct mdp_ipi_comm_ack` are the transport messages. `struct mdp_config`, `struct mdp_buffer`, `struct mdp_config_misc`, and `struct mdp_process_vsi` describe source/destination crop/format/buffers and rotation/flip/alpha settings. `MTK_MDP_MAX_NUM_PLANE` fixes the plane count at three.

## Control Flow
The AP sends init to allocate/map a VPU instance, fills the shared `mdp_process_vsi`, then sends process/deinit messages. The VPU replies with ack messages containing status and instance address.

## State and Persistence
The packed structures represent shared memory and mailbox payload state. They persist only while the VPU instance exists and must match firmware layout exactly.

## Dependencies and Integration Points
This ABI is included by `mtk_mdp_vpu.h`, `mtk_mdp_vpu.c`, and register helper code. It couples the kernel driver to the MediaTek VPU firmware implementation.

## Risks and Edge Cases
Packed structure layout, field sizes, and message IDs are firmware ABI; changing them breaks AP/VPU communication. Buffer addresses are 64-bit MVA values even when other fields are 32-bit, so alignment and endian assumptions matter.

## Test Signals
IPI init/process/deinit round trips, firmware status failures, shared-memory dump comparisons, and cross-architecture structure-size checks are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_ipi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_m2m.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_m2m.c

## Purpose
This file implements the legacy MDP V4L2 mem2mem frontend. It exposes formats, controls, crop/compose selection, vb2 queue operations, per-file context setup, VPU firmware initialization, and the job worker that fills the VPU shared configuration and runs processing.

## Important APIs, Types, and Functions
Format/limit data include `mtk_mdp_formats[]`, size alignments, and the default variant. Key helpers are format lookup/try/set, crop validation, scaler-ratio checking, queue setup/prepare/streaming, address preparation, `mtk_mdp_m2m_worker()`, `mtk_mdp_process_done()`, control creation and `mtk_mdp_s_ctrl()`. Public registration APIs are `mtk_mdp_register_m2m_device()` and `mtk_mdp_unregister_m2m_device()`.

## Control Flow
Open allocates a context, initializes controls and V4L2 file handle, creates a mem2mem context, loads/registers VPU firmware on the first active context, adds the context to `ctx_list`, and sets default formats. Streaming initializes the VPU instance on first use. The mem2mem scheduler queues `ctx->work`; the worker checks error state, maps current source/destination vb2 buffers to DMA addresses, fills source/destination size/format/address and misc controls into the VPU shared structure, sends `AP_MDP_PROCESS`, and completes both buffers with DONE or ERROR. Stop streaming drains queued buffers as errors and drops runtime PM.

## State and Persistence
Per-context state includes source/destination frame formats/crops/payloads, controls, colorimetry, VPU instance and shared memory pointer, mem2mem queues, and error flags. Device state tracks active context count and the job workqueue. No user configuration persists across close.

## Dependencies and Integration Points
The frontend depends on V4L2 ioctl/mem2mem, vb2 DMA-contig, runtime PM, the VPU firmware loader/IPI path, and helper functions from `mtk_mdp_regs.c` that populate `ctx->vpu.vsi`. It registers a `/dev/video*` M2M node named `mtk-mdp:m2m`.

## Risks and Edge Cases
`mtk_mdp_check_scaler_ratio()` uses integer division, so ratios below 1 truncate and boundary cases need testing. Format defaults and payload calculations must match multi-plane and single-plane YUV addressing, especially `YVU420` synthetic plane offsets. `mtk_mdp_s_ctrl()` checks rotation using the current control value rather than the incoming value in a subtle way. Release always calls VPU deinit even if init failed or streaming never started. Workqueue flushing on release serializes all jobs, so long VPU operations can delay close.

## Test Signals
Use v4l2-compliance, all advertised formats, single-plane and multi-plane YUV buffers, crop/compose with rotation, scaler-ratio limits, runtime PM start/stop balance, multiple contexts, VPU process failures, watchdog error state, and streamoff with queued buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_m2m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_m2m.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_m2m.h

## Purpose
This header exposes the legacy MDP mem2mem registration and context-state helper used by the core and watchdog paths.

## Important APIs, Types, and Functions
It declares `mtk_mdp_ctx_state_lock_set()`, `mtk_mdp_register_m2m_device()`, and `mtk_mdp_unregister_m2m_device()`.

## Control Flow
The core calls registration during probe and unregister during remove. The watchdog calls the state setter to mark active contexts as error.

## State and Persistence
The header itself holds no state; it gives access to context state mutation and video-device lifecycle.

## Dependencies and Integration Points
It depends on `struct mtk_mdp_ctx` and `struct mtk_mdp_dev` from `mtk_mdp_core.h`.

## Risks and Edge Cases
Callers must hold appropriate lifecycle references to contexts/devices because the prototypes do not encode ownership. State setting only ORs bits; it does not clear errors.

## Test Signals
Compile/link coverage and watchdog-triggered error-state tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_m2m.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_regs.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_regs.c

## Purpose
Despite its name, this file does not directly program MMIO registers. It translates V4L2 context/frame settings into the legacy VPU shared `mdp_process_vsi` structure for source/destination buffers, crop, formats, rotation/flip, and alpha.

## Important APIs, Types, and Functions
The exported helpers are `mtk_mdp_hw_set_input_addr()`, `mtk_mdp_hw_set_output_addr()`, `mtk_mdp_hw_set_in_size()`, `mtk_mdp_hw_set_in_image_format()`, `mtk_mdp_hw_set_out_size()`, `mtk_mdp_hw_set_out_image_format()`, `mtk_mdp_hw_set_rotation()`, and `mtk_mdp_hw_set_global_alpha()`. `mtk_mdp_map_color_format()` maps V4L2 fourccs to firmware `MDP_COLOR_*` encodings.

## Control Flow
The mem2mem worker prepares DMA addresses in frames, then calls these helpers in sequence before `mtk_mdp_vpu_process()`. Each helper writes the corresponding fields in `ctx->vpu.vsi`.

## State and Persistence
The state written here is shared-memory job state consumed by VPU firmware. It is overwritten for each queued job and does not persist after context deinit.

## Dependencies and Integration Points
The file depends on `mtk_mdp_core.h`, `mtk_mdp_regs.h`, and the IPI structs from `mtk_mdp_ipi.h`. It is the conversion point from Linux V4L2 formats/crops to firmware ABI.

## Risks and Edge Cases
Unsupported formats map to `MDP_COLOR_UNKNOWN` after logging, but callers do not get an explicit error at this layer. Stride fields are set to zero so firmware must infer them from color format and plane sizes. Plane size loops use `plane_num` from format metadata and must stay within `MTK_MDP_MAX_NUM_PLANE`.

## Test Signals
Verify VPU shared memory for each supported fourcc, crop geometry, plane size, rotation, hflip/vflip, and global alpha before processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_regs.h

## Purpose
This header declares the legacy MDP helpers that fill VPU shared processing state from a V4L2 context.

## Important APIs, Types, and Functions
It declares setters for input/output addresses, source/destination sizes, source/destination image formats, rotation/flip, and global alpha.

## Control Flow
The mem2mem worker includes this header and calls all setters before sending a VPU process message.

## State and Persistence
No state is stored here; the declared functions mutate `ctx->vpu.vsi`.

## Dependencies and Integration Points
The declarations depend on `struct mtk_mdp_ctx` and `struct mtk_mdp_addr` from the core header.

## Risks and Edge Cases
The API assumes `ctx->vpu.vsi` has been mapped by VPU init before calls. There is no static protection against calling setters out of order.

## Test Signals
Compile/link coverage plus process tests that inspect populated VPU shared data validate the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_vpu.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_vpu.c

## Purpose
This file implements legacy MDP communication with the MediaTek VPU over IPI. It registers the MDP IPI handler, sends init/process/deinit messages, maps VPU shared memory, and records firmware status.

## Important APIs, Types, and Functions
Public APIs are `mtk_mdp_vpu_register()`, `mtk_mdp_vpu_init()`, `mtk_mdp_vpu_process()`, and `mtk_mdp_vpu_deinit()`. Internal helpers convert `struct mtk_mdp_vpu` to its context, handle init acknowledgements by mapping the VPU instance address, dispatch IPI acks, and serialize sends under `mdp_dev->vpulock`.

## Control Flow
On first context open, the driver registers an IPI handler. Stream-on calls init, which sends `AP_MDP_INIT`; the ack stores the firmware instance address and maps `vsi`. Each job sends `AP_MDP_PROCESS`; release sends `AP_MDP_DEINIT`. All sends check immediate IPI errors and the latest firmware failure status.

## State and Persistence
`struct mtk_mdp_vpu` stores the VPU platform device, firmware instance address, last failure code, and mapped shared `mdp_process_vsi` pointer. This state is per context and lasts until deinit/release.

## Dependencies and Integration Points
The code depends on `mtk_vpu.h` APIs: `vpu_ipi_register()`, `vpu_ipi_send()`, and `vpu_mapping_dm_addr()`. It integrates with context/device state from `mtk_mdp_core.h` and message definitions in `mtk_mdp_ipi.h`.

## Risks and Edge Cases
The IPI handler trusts `ap_inst` from firmware to be a valid kernel pointer. `vpu->failure` is shared between asynchronous acks and send callers without an explicit completion object here, relying on VPU send semantics. Unknown ack IDs are logged but not fatal if status is zero. A missing `vpu->pdev` returns `-EINVAL`.

## Test Signals
Firmware load/register, init ack mapping, process/deinit ack status failures, concurrent contexts serialized by `vpulock`, and VPU reset behavior are key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_vpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_vpu.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_vpu.h

## Purpose
This header defines per-context VPU state and declares the legacy MDP VPU transport functions.

## Important APIs, Types, and Functions
`struct mtk_mdp_vpu` stores the VPU platform device, firmware instance address, failure status, and shared `mdp_process_vsi` pointer. Declared functions register the IPI handler and send init/process/deinit requests.

## Control Flow
The mem2mem frontend owns a `struct mtk_mdp_vpu` in each context and calls these functions during stream-on, job execution, and release.

## State and Persistence
The structure is per context and persists for the open file/streaming lifetime.

## Dependencies and Integration Points
It includes `mtk_mdp_ipi.h` for the shared-memory ABI and is included by the core context definition.

## Risks and Edge Cases
Callers must not use `vsi` before init succeeds. The header does not enforce send ordering.

## Test Signals
Compile/link checks and stream lifecycle tests validate the state contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp/mtk_mdp_vpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/Kconfig

## Purpose
This Kconfig entry exposes the newer MediaTek MDP v3 V4L2 mem2mem driver.

## Important APIs, Types, and Functions
The symbol is `VIDEO_MEDIATEK_MDP3`, a tristate option depending on IOMMU/compile-test, video device support, DMA, remoteproc, MediaTek MMSYS, CMDQ, and SCP. It selects vb2 DMA-contig and V4L2 mem2mem support.

## Control Flow
When enabled, Kbuild compiles the `mtk-mdp3` aggregate object from the Makefile. Runtime behavior is split across core, VPU, regs, mem2mem, component, and CMDQ files.

## State and Persistence
The selected value persists in `.config` and controls built-in/module/disabled driver state.

## Dependencies and Integration Points
MDP3 requires the SCP firmware path, command queue mailbox engine, MMSYS routing, DMA/IOMMU, and V4L2/vb2 infrastructure.

## Risks and Edge Cases
The dependencies are stricter than the legacy driver because runtime CMDQ and SCP are central. Compile-test coverage must keep these dependencies satisfiable across architectures.

## Test Signals
Use MediaTek SoC defconfigs, `allmodconfig`, `COMPILE_TEST`, and dependency warning checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/Makefile

## Purpose
This Makefile aggregates the MDP3 driver sources into the `mtk-mdp3` module/built-in object.

## Important APIs, Types, and Functions
It builds `mdp_cfg_data.o`, `mtk-mdp3-core.o`, `mtk-mdp3-vpu.o`, `mtk-mdp3-regs.o`, `mtk-mdp3-m2m.o`, `mtk-mdp3-comp.o`, and `mtk-mdp3-cmdq.o` under `obj-$(CONFIG_VIDEO_MEDIATEK_MDP3)`.

## Control Flow
Kbuild includes the aggregate object only when the Kconfig symbol is enabled.

## State and Persistence
No runtime state exists; the file defines build composition.

## Dependencies and Integration Points
The object list must stay synchronized with source files and Kconfig dependencies.

## Risks and Edge Cases
Missing one translation unit can break link-time symbols or silently remove runtime functionality such as CMDQ packet generation.

## Test Signals
Targeted driver builds and `allmodconfig` catch stale object references and unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_cfg_data.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_cfg_data.c

## Purpose
This file is the static SoC configuration database for MDP3. It maps public component IDs to SCP inner IDs, component types, aliases, MM subsystem IDs, clock/resource metadata, blend/auxiliary components, supported V4L2 formats, image limits, pipe/mutex routing, probe infrastructure, and per-platform feature flags for MT8183, MT8188, and MT8195-family data.

## Important APIs, Types, and Functions
It defines internal component-ID enums, `mdp_platform_config` instances, mutex-index tables, `mdp_comp_data` arrays, subcomponent DT match tables, format arrays, default limits, pipe-info arrays, and exported driver-data objects `mt8183_mdp_driver_data`, `mt8188_mdp_driver_data`, and `mt8195_mdp_driver_data`. Lookup helpers are `mdp_cfg_get_id_inner()`, `mdp_cfg_get_id_public()`, and `mdp_cfg_comp_is_dummy()`.

## Control Flow
The core chooses one exported driver-data object from OF match data. Component discovery uses `comp_data` and alias counters to bind DT nodes to public IDs. CMDQ path building uses the pipe/mutex tables and platform flags. V4L2 mem2mem uses the format arrays and default limits for negotiation. SCP configuration uses the inner/public ID mapping.

## State and Persistence
Most data is immutable static const configuration. The lookup helpers read current `mdp_dev->mdp_data`. There is no runtime persistence beyond the selected pointer in the probed device.

## Dependencies and Integration Points
The file depends on `mtk-img-ipi.h`, `mtk-mdp3-core.h`, `mtk-mdp3-comp.h`, and register/type definitions. It integrates device-tree compatibles, MMSYS/mutex indices, SCP platform IDs, V4L2 fourccs, and component operation code.

## Risks and Edge Cases
The tables must remain internally consistent: public ID, inner ID, alias order, DT node order, mutex index, pipe info, and shared-memory layout all have to agree. `mdp_cfg_get_id_public()` treats `inner_id == 0` as invalid, so components with zero inner IDs are intentionally not returned by that path. `mdp_cfg_comp_is_dummy()` indexes `comp_data[id]` after lookup and assumes the lookup did not return `MDP_COMP_NONE` in a way that underflows. MT8188 reuses MT8195 platform config/format/limits, which must remain valid for both SoCs.

## Test Signals
Probe tests on each supported SoC, DT alias ordering tests, component discovery logs, V4L2 format enumeration, pipe/mutex routing for one- and two-postprocessor jobs, and SCP-generated config validation are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_cfg_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_aal.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_aal.h

## Purpose
This header defines MDP3 AAL block register offsets and write masks for adaptive ambient/light processing or relay configuration.

## Important APIs, Types, and Functions
It exports macros for enable, configuration, input/output size, output offset, and main config registers plus their masks.

## Control Flow
`mtk-mdp3-comp.c` uses these macros in AAL init/frame/subframe operations to enable the block and apply SCP-provided tile geometry/configuration through CMDQ writes.

## State and Persistence
The macros describe volatile AAL MMIO state programmed per frame/subframe.

## Dependencies and Integration Points
The header is included only by component programming code and must match the MDP3 hardware register map.

## Risks and Edge Cases
Mask errors can overwrite reserved bits. Size/offset masks imply 13-bit dimensions and limited offset fields, so SCP-generated values must fit.

## Test Signals
CMDQ packet inspection and MT8195 AAL path tests with tile offsets/sizes validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_aal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_ccorr.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_ccorr.h

## Purpose
This header defines CCORR register offsets and masks for MDP3 color-correction relay/size programming.

## Important APIs, Types, and Functions
Macros cover enable, config, and size registers plus masks.

## Control Flow
The CCORR component ops enable relay mode and write tile size during subframe configuration.

## State and Persistence
The state is volatile CCORR MMIO state for each command queue job.

## Dependencies and Integration Points
Included by `mtk-mdp3-comp.c`, primarily for MT8183 CCORR support.

## Risks and Edge Cases
The size mask encodes two 13-bit dimensions; invalid tile widths/heights from SCP would be truncated by masked writes.

## Test Signals
MT8183 CCORR relay paths and CMDQ register dumps are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_ccorr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_color.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_color.h

## Purpose
This header defines MDP3 COLOR block offsets and masks for start, interrupt, output selection, internal image size, and color-matrix enable registers.

## Important APIs, Types, and Functions
Macros include window positions, `MDP_COLOR_START`, interrupt enable, output select, internal width/height, and CM enable masks.

## Control Flow
Component init resets matrix state, enables interrupts and output selection; frame/subframe ops program start and internal tile dimensions.

## State and Persistence
Volatile COLOR block register state is configured per CMDQ job.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c` for MT8195 COLOR components in SCP-generated paths.

## Risks and Edge Cases
Incorrect start/out-select bits can stall downstream components. Width/height masks must match tile geometry range.

## Test Signals
Color relay/path jobs, interrupt/event completion, and register trace validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_color.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_fg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_fg.h

## Purpose
This header defines MDP3 FG block register offsets and masks for trigger, control, clock-enable, and tile information programming.

## Important APIs, Types, and Functions
Macros cover `MDP_FG_TRIGGER`, `MDP_FG_FG_CTRL_0`, `MDP_FG_FG_CK_EN`, and two tile-info registers.

## Control Flow
FG component ops pulse reset/trigger, configure frame control/clock bits, then write tile info per subframe.

## State and Persistence
The state is volatile FG MMIO state per command queue job.

## Dependencies and Integration Points
Included by `mtk-mdp3-comp.c` for MT8195/MT8188 foreground blocks.

## Risks and Edge Cases
Trigger/control mask mistakes can leave the block disabled or clock-gated. Tile-info fields are full-width and rely entirely on SCP correctness.

## Test Signals
FG-enabled pipeline CMDQ dumps and output comparison against relay/bypass expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_fg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_hdr.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_hdr.h

## Purpose
This header defines MDP3 HDR block register offsets and masks for top/relay control, size windows, histogram controls, histogram address, and tile position.

## Important APIs, Types, and Functions
Macros include `MDP_HDR_TOP`, `MDP_HDR_RELAY`, `MDP_HDR_SIZE_0..2`, histogram controls/address, and tile position masks.

## Control Flow
HDR component ops enable the block, set relay/top frame bits, then program per-subframe tile size, clipping offsets, histogram controls, and histogram enable/address.

## State and Persistence
HDR register state is volatile and programmed through CMDQ for each job/subframe.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c` and SCP shared-memory structs for MT8195 HDR paths.

## Risks and Edge Cases
Histogram fields are sensitive to buffer/address setup not visible in this header. Mask drift can corrupt reserved HDR controls.

## Test Signals
HDR-enabled pipelines, histogram buffer validation, and register traces are high-value tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_hdr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_merge.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_merge.h

## Purpose
This header defines MDP3 MERGE block offsets and masks used when RSZ2/RSZ3 paths require merge assistance on MT8195-like platforms.

## Important APIs, Types, and Functions
Macros include enable and several config registers: `MDP_MERGE_CFG_0`, `_4`, `_12`, `_24`, and `_25`, all with full-width masks.

## Control Flow
RSZ subframe configuration writes merge config registers, enables bypass mode, and turns on MERGE when the selected RSZ path has a companion merge block.

## State and Persistence
MERGE MMIO state is volatile and per path/subframe.

## Dependencies and Integration Points
Used by RSZ operations in `mtk-mdp3-comp.c` together with MMSYS RSZ merge routing.

## Risks and Edge Cases
Full-width writes make SCP-provided values and register-map accuracy critical. Missing companion merge components break RSZ2/RSZ3 setup.

## Test Signals
Dual-pipe or RSZ2/RSZ3 jobs, MMSYS merge routing traces, and CMDQ register dumps validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_merge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_ovl.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_ovl.h

## Purpose
This header defines MDP3 OVL block offsets and masks for overlay relay/layer sizing used in advanced MT8195 paths.

## Important APIs, Types, and Functions
Macros cover enable, ROI size, datapath control, source control, layer 0 control, and layer 0 source size.

## Control Flow
OVL component ops enable relay mode during init, configure layer/source frame bits, and write ROI/source size per subframe.

## State and Persistence
The OVL state is volatile command-queue-programmed MMIO state.

## Dependencies and Integration Points
Included by `mtk-mdp3-comp.c` for OVL components selected by static SoC data.

## Risks and Edge Cases
Overlay relay setup must match downstream ROI sizes or paths can hang/produce clipped output. Reserved-bit masks must stay correct.

## Test Signals
OVL path CMDQ traces and output-size validation across tiled subframes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_ovl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_pad.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_pad.h

## Purpose
This header defines MDP3 padding block offsets and masks for padding control and picture/width/height size registers.

## Important APIs, Types, and Functions
Macros cover `MDP_PAD_CON`, `MDP_PAD_PIC_SIZE`, `MDP_PAD_W_SIZE`, and `MDP_PAD_H_SIZE`.

## Control Flow
PAD component ops initialize the block, clear width/height sizes, and program picture size per subframe.

## State and Persistence
State is volatile PAD block MMIO state.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c` for MT8195/MT8188 pad components.

## Risks and Edge Cases
Padding geometry comes from SCP and is written directly; invalid dimensions can affect downstream components.

## Test Signals
PAD-enabled path register dumps and output dimension tests validate use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_pad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_rdma.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_rdma.h

## Purpose
This header defines the MDP3 RDMA register map and masks for source DMA, cropping, transform, UFO/10-bit data, SMI/pre-ultra thresholds, and event/status handling.

## Important APIs, Types, and Functions
Macros cover enable/reset/control, GMCIF, source format/control, background/source/clip sizes, offsets, transform, DMA buffer thresholds, monitor status, base/end addresses, and UFO decode length bases.

## Control Flow
RDMA component ops reset the block, configure source format/address/pitch/transform/ESL thresholds at frame scope, configure offsets/source/clip per subframe, enable RDMA, wait for EOF, and disable it.

## State and Persistence
RDMA register state is volatile and reprogrammed through CMDQ per job.

## Dependencies and Integration Points
Used heavily by `mtk-mdp3-comp.c`; field values come from SCP shared-memory config generated for MT8183/MT8195 layouts.

## Risks and Edge Cases
RDMA touches DMA addresses and memory pressure thresholds, so mask or address mistakes can cause memory faults or underruns. 10-bit/UFO paths require matching color-format flags and extra address registers. Reset polling relies on hardware status bit semantics.

## Test Signals
RDMA reset/EOF events, IOMMU fault absence, 10-bit/UFO formats, multi-plane formats, tiled subframes, and ESL threshold register traces are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_rsz.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_rsz.h

## Purpose
This header defines MDP3 resizer register offsets and masks for enable/reset, control, input/output size, coefficient steps, luma/chroma offsets, and extra control.

## Important APIs, Types, and Functions
Macros include `PRZ_ENABLE`, `PRZ_CONTROL_1/2`, input/output image, horizontal/vertical coefficient steps, integer/subpixel luma and chroma offsets, and `RSZ_ETC_CONTROL`.

## Control Flow
RSZ component ops reset/enable the block, configure frame-level scaling controls and coefficients, program per-subframe source/output sizes and subpixel offsets, optionally coordinate merge blocks, and undo DCM workarounds.

## State and Persistence
RSZ register state is volatile per CMDQ job.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c` and MMSYS RSZ merge routing on MT8195-like platforms.

## Risks and Edge Cases
Subpixel offsets and coefficient steps must match SCP scaler calculations. DCM/merge workarounds are platform-flag dependent. Small-sample and bypass paths need separate coverage.

## Test Signals
Scale-up/down, bypass, small-sample, RSZ2/RSZ3 merge, and subframe tiling tests validate this map.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_rsz.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_tdshp.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_tdshp.h

## Purpose
This header defines TDSHP sharpness/histogram register offsets and masks for MDP3 display-quality processing.

## Important APIs, Types, and Functions
Macros cover histogram config, control/config, input/output size/offset, luma histogram initialization, constrain result initialization, and contour histogram initialization.

## Control Flow
TDSHP ops enable the block/FIFO, reset histogram memories, apply frame config, and write per-subframe input/output and histogram configuration.

## State and Persistence
Histogram and TDSHP configuration state is volatile but may retain values across jobs unless reset by init operations.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c`, with histogram counts and constraints controlled by platform flags from `mdp_cfg_data.c`.

## Risks and Edge Cases
Histogram reset loops depend on `tdshp_hist_num`; off-by-one errors can leave stale histogram state. Mask drift can affect image quality or processing hangs.

## Test Signals
TDSHP-enabled pipelines, histogram reset traces, contour/constrain platform variants, and output comparison tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_tdshp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_wdma.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_wdma.h

## Purpose
This header defines MDP3 WDMA register offsets and masks for destination DMA output without rotation.

## Important APIs, Types, and Functions
Macros cover enable/reset/config, source and clip geometry, destination pitches, alpha, buffer controls, plane offsets, flow-control debug, and destination base addresses.

## Control Flow
WDMA ops reset the block, program frame buffer addresses/pitches/config/alpha, program subframe offsets/source/clip/coordinate, enable WDMA, wait EOF, and disable it.

## State and Persistence
WDMA MMIO state is volatile per job/subframe.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c`, primarily for MT8183 WDMA paths in the current implementation.

## Risks and Edge Cases
Address/offset mistakes can corrupt output buffers. Reset polling uses flow-control status. The current component code reads WDMA shared fields only under MT8183 checks, so MT8195 WDMA use would need review.

## Test Signals
WDMA output jobs, multi-plane offsets, alpha, reset/EOF events, and IOMMU fault monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_wdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_wrot.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_wrot.h

## Purpose
This header defines MDP3 WROT register offsets and masks for rotated/scaled output DMA.

## Important APIs, Types, and Functions
Macros cover control, buffer size, soft reset/status, crop/target size, plane offsets/strides, dither, pre-ultra, input size, rotation enable, FIFO, matrix, 10-bit scan, pending-zero, and base addresses.

## Control Flow
WROT ops reset the block, program frame base addresses/strides/control/matrix/fifo/10-bit/pre-ultra settings, program subframe offsets/source/target/crop/main-buffer fields, enable rotation output, wait EOF, and disable it.

## State and Persistence
WROT register state is volatile but reset at job start.

## Dependencies and Integration Points
Used by `mtk-mdp3-comp.c`; values come from SCP shared-memory layouts and platform flags.

## Risks and Edge Cases
Soft reset polling, DMA address offsets, 10-bit fields, and filter constraints are sensitive hardware paths. Output rotation and stride must match V4L2 compose/crop state.

## Test Signals
0/90/180/270 rotation jobs, 10-bit output, multi-plane strides, filter-constraint variants, EOF event timing, and output buffer integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_reg_wrot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_sm_mt8183.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_sm_mt8183.h

## Purpose
This header defines the packed SCP/AP shared-memory configuration layout for MT8183 MDP3 processing.

## Important APIs, Types, and Functions
It defines `IMG_MAX_SUBFRAMES_8183`, common component frame/subframe structs, per-block data for RDMA, RSZ, WROT, WDMA, ISP metadata, `struct img_compparam_8183`, and `struct img_config_8183`.

## Control Flow
SCP firmware fills this layout in shared memory. Kernel CMDQ code reads it through `CFG_GET`, `CFG_COMP`, and `CFG_ADDR` macros to configure component contexts, frame registers, subframe registers, MMSYS controls, and mutex routing.

## State and Persistence
The packed structures are per-frame/job shared state. They persist only until overwritten by the next SCP frame configuration.

## Dependencies and Integration Points
It includes `mtk-mdp3-type.h` for shared primitive geometry and enum limits and is unioned into `struct img_config`/`img_compparam` in `mtk-img-ipi.h`.

## Risks and Edge Cases
This is firmware ABI. Packing, field width, array size, and MD5-tagged SCP prebuild compatibility must remain exact. MT8183 supports fewer subframes and component data types than MT8195.

## Test Signals
Structure size/layout checks against SCP firmware, MT8183 frame processing, maximum subframe count, and CMDQ field extraction traces validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_sm_mt8183.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_sm_mt8195.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_sm_mt8195.h

## Purpose
This header defines the packed SCP/AP shared-memory configuration layout for MT8195-class MDP3 processing, also reused by MT8188 driver data.

## Important APIs, Types, and Functions
It defines `IMG_MAX_SUBFRAMES_8195`, 32-bit component frame/subframe structures, per-block data for RDMA, FG, HDR, AAL, RSZ, TDSHP, COLOR, OVL, PAD, TCC, WROT, WDMA, ISP metadata, `struct img_compparam_8195`, and `struct img_config_8195`.

## Control Flow
SCP-generated config is read by CMDQ path and component code to program every block. The extra fields support multi-RDMA, multi-postprocessor, merge, HDR/PQ, 10-bit, ESL, and advanced VPP routing features.

## State and Persistence
These packed structures are per-frame shared-memory state and are overwritten per job.

## Dependencies and Integration Points
It includes `mtk-mdp3-type.h` and is selected through `struct img_config`/`img_compparam` unions in `mtk-img-ipi.h`. Component ops in `mtk-mdp3-comp.c` read many of its nested fields.

## Risks and Edge Cases
The ABI must match the SCP prebuild MD5 noted in the file. Array bounds depend on `IMG_MAX_SUBFRAMES_8195` and `IMG_MAX_COMPONENTS`. Adding fields or changing packing breaks firmware/kernel compatibility.

## Test Signals
MT8195/MT8188 SCP config dumps, maximum subframe paths, dual postprocessor jobs, advanced block enablement, and structure-size assertions are useful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mdp_sm_mt8195.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-img-ipi.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-img-ipi.h

## Purpose
This header defines the generic image IPI/frame parameter ABI used by MDP3 between the AP kernel driver and SCP firmware, plus platform-dispatch macros for MT8183 and MT8195 shared config layouts.

## Important APIs, Types, and Functions
It defines IPI message IDs, packed address/time/pixel-format/image-buffer/input/output/frameparam structures, `img_ipi_param`, `img_frameparam`, platform IDs, `CFG_CHECK`, `CFG_OFST`, `CFG_ADDR`, `CFG_GET`, `CFG_COMP`, and union wrappers `struct img_config` and `struct img_compparam`.

## Control Flow
The MDP3 VPU/SCP path exchanges `img_ipi_frameparam` and config buffers. CMDQ code uses the CFG macros to select the right packed layout based on `mdp_plat_id` and to index per-postprocessor config blocks.

## State and Persistence
Frame parameters, config/self/tuning buffer addresses, and image buffers are per-job shared state. They are not persistent beyond processing and buffer lifetime.

## Dependencies and Integration Points
It includes MT8183/MT8195 shared-memory headers and `mtk-mdp3-type.h`. It is included by CMDQ, config, and VPU/core paths.

## Risks and Edge Cases
Packed ABI structs carry kernel virtual, CM4 physical, and IOMMU addresses in adjacent fields; using the wrong address domain can break firmware or hardware. CFG pointer arithmetic must stay within `mdp->vpu.config_size`, as guarded in CMDQ code. MT8188 is represented with platform value 8195 for config layout purposes.

## Test Signals
IPI frame submission, config-buffer bounds checks, address-domain validation, dual-output frames, and platform macro dispatch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-img-ipi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cfg.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cfg.h

## Purpose
This header exposes MDP3 SoC driver-data objects and component-ID lookup helpers.

## Important APIs, Types, and Functions
It declares `mt8183_mdp_driver_data`, `mt8188_mdp_driver_data`, and `mt8195_mdp_driver_data`, forward-declares `struct mdp_dev` and `enum mtk_mdp_comp_id`, and declares inner/public/dummy lookup helpers.

## Control Flow
The core selects one driver-data object at probe. Component and CMDQ code call lookup helpers to translate SCP inner IDs to kernel public IDs and to skip dummy path-only components.

## State and Persistence
The header itself is stateless. The declared driver data are immutable static data in `mdp_cfg_data.c`.

## Dependencies and Integration Points
It is included by core, CMDQ, component, and config data files.

## Risks and Edge Cases
Lookup helpers depend on a valid `mdp_dev->mdp_data`; callers must avoid using them before probe data is installed.

## Test Signals
Compile/link coverage and SoC-specific component discovery tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cmdq.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cmdq.c

## Purpose
This file converts SCP-generated MDP3 frame/config data into command queue packets. It builds component paths, programs MMSYS muxing, configures frame/subframe component registers through operation tables, prepares mutexes, sends packets via mailbox CMDQ clients, and releases clocks/mutexes on callbacks.

## Important APIs, Types, and Functions
`struct mdp_path` is the transient path builder. `mdp_cmdq_send()` is the exported entry. Internal helpers select postprocessor count, pipe/mutex, config offsets, path contexts, subframe requirements/runs, full path configuration, command preparation, and callback cleanup. `mdp_handle_cmdq_callback()` queues `mdp_auto_release_work()` for clock/mutex release and user callback/job finish.

## Control Flow
`mdp_cmdq_send()` sets a job refcount, rejects suspended devices, prepares one or two CMDQ commands depending on stream type, turns on component clocks, syncs command buffers for DMA, and sends mailbox messages. Preparation bounds-checks per-PP config, creates a packet, builds component contexts from shared config, prepares the selected mutex, runs frame setup, loops over subframes to program muxes/components/mutex/EOF waits/advance hooks, appends EOC and jump, copies component descriptors for cleanup, and installs the mailbox callback. Callback work unprepares the mutex, disables clocks, decrements job count, finishes mem2mem/user callbacks when the last PP completes, destroys packets, and frees allocations.

## State and Persistence
Runtime state is transient in `mdp_cmdq_cmd`, `mdp_path`, copied component arrays, command packets, and `mdp->job_count`. Hardware state persists only in the submitted CMDQ sequence until callback cleanup. No durable state is stored.

## Dependencies and Integration Points
The file depends on CMDQ mailbox APIs, MediaTek mutex/MMSYS helpers, MDP3 component ops, config data, MDP3 core state, V4L2 compose rectangles, and SCP shared config layouts from `mtk-img-ipi.h`.

## Risks and Edge Cases
`is_output_disabled()` currently reads `frame.output_disable` for both output and tile-disable decisions, which may be intentional ABI aliasing or a bug. `mdp_cmdq_prepare()` obtains `num_comp` from `param->config` rather than the PP-specific `config` pointer, which is subtle for dual-PP layouts. Error paths after some clocks are enabled may not destroy all prepared packets because `err_clock_off` only walks down from the failing index. Callback cleanup relies on `cmd->comps[0]` being valid and non-dummy. Refcount/job finish behavior must be correct for dual-bitblt jobs.

## Test Signals
Single- and dual-PP jobs, suspended-device cancellation, invalid config offset, dummy components, disabled output subframes, CMDQ packet decode, mailbox send failure, callback ordering, clock/mutex balance, and mem2mem job completion are critical tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cmdq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cmdq.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cmdq.h

## Purpose
This header defines the public command-queue submission contract for MDP3.

## Important APIs, Types, and Functions
`struct mdp_cmdq_param` packages SCP config, frame parameters, output compose rectangles, optional user callback/data, and mem2mem context. `struct mdp_cmdq_cmd` stores the in-flight CMDQ packet, callback work, event pointer, device, callback data, copied component list, context, PP index, and component count. `mdp_cmdq_send()` submits work.

## Control Flow
Higher layers fill `mdp_cmdq_param` after SCP frame configuration and call `mdp_cmdq_send()`. The implementation allocates `mdp_cmdq_cmd` instances and frees them after mailbox callback cleanup.

## State and Persistence
The parameter is caller-owned per job. `mdp_cmdq_cmd` is in-flight state owned by the CMDQ implementation until callback release.

## Dependencies and Integration Points
It includes platform device, V4L2, MediaTek CMDQ, and image IPI definitions. It forward-declares `struct mdp_dev`.

## Risks and Edge Cases
The callback/data pointers are raw and must remain valid according to the submission contract. `config`, `param`, and compose pointers must cover all outputs and PP indices.

## Test Signals
Compile coverage, callback invocation tests, and job cancellation/error-path tests validate this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-cmdq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-comp.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-comp.c

## Purpose
This file implements MDP3 component discovery, clock/runtime-PM control, component context binding, and per-component CMDQ register programming operations. It covers RDMA, RSZ, WROT, WDMA, TDSHP, COLOR, CCORR, AAL, HDR, FG, OVL, PAD, and merge-assisted paths.

## Important APIs, Types, and Functions
The central operation tables are `rdma_ops`, `rsz_ops`, `wrot_ops`, `wdma_ops`, `tdshp_ops`, `color_ops`, `ccorr_ops`, `aal_ops`, `hdr_ops`, `fg_ops`, `ovl_ops`, and `pad_ops`, collected in `mdp_comp_ops[]`. Public APIs include `mdp_comp_config()`, `mdp_comp_destroy()`, `mdp_comp_clocks_on()`, `mdp_comp_clocks_off()`, `mdp_comp_clock_on()`, `mdp_comp_clock_off()`, and `mdp_comp_ctx_config()`. Static helpers bind DT nodes to `struct mdp_comp`, read CMDQ subsys IDs/events, map aliases to public IDs, and handle platform flags.

## Control Flow
Probe-time `mdp_comp_config()` scans sibling DT nodes, matches component compatibles, assigns alias IDs, creates components, gets clocks/MMIO/CMDQ subsys IDs/GCE events, enables runtime PM for DMA-capable blocks, and then creates subcomponents. At job time, CMDQ path setup calls `mdp_comp_ctx_config()` to bind SCP component params to actual components and frame inputs/outputs. Component ops reset/init blocks, write frame-level state, write subframe/tile state, wait EOF events for DMA blocks, optionally advance subframes, and postprocess through CMDQ macros.

## State and Persistence
Persistent device-lifetime state is in `mdp->comp[]` entries: component device, public/inner/alias IDs, type, reg base, mapped regs, clocks, subsys ID, GCE events, ops, and MDP backpointer. Global static state includes alias counters and `p_id`, set during component config. In-flight state is `struct mdp_comp_ctx`, which points at shared SCP params and frame inputs/outputs.

## Dependencies and Integration Points
The file depends on OF/platform device lookup, clocks, runtime PM, CMDQ client register lookup, MediaTek MMSYS helpers, MDP3 config data, register headers for each block, and SCP shared-memory structures. It is called by core probe/remove and CMDQ path construction.

## Risks and Edge Cases
The global `p_id` and alias counters assume one active platform configuration path at a time. `mdp_comp_destroy()` frees components with `devm_kfree(mdp->comp[i]->comp_dev, ...)` even though allocation used the parent MDP device, which deserves lifecycle review. `mdp_comp_clocks_on()` does not unwind previously enabled components if a later component or auxiliary blend clock fails. Missing EOF GCE events are fatal only for DMA-capable components. WDMA programming is MT8183-only in several reads. Full correctness depends on SCP-generated fields matching the selected SoC ABI and register masks.

## Test Signals
Probe on MT8183/MT8188/MT8195 DTs, missing clocks/events, runtime PM balance, component alias ordering, CMDQ packet inspection for every component type, 10-bit/UFO RDMA, RSZ merge paths, WROT rotations, WDMA output, HDR/AAL/TDSHP/FG/OVL/PAD paths, mailbox error unwind, and remove/unbind leak checks are the best validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/mdp3/mtk-mdp3-comp.c -->
