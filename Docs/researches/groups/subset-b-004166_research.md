# Research: subset-b-004166

Work item `subset-b-004166` covers Samsung JPEG register definitions plus the Samsung S5P/Exynos MFC V4L2 codec driver core, command layer, decoder path, and generation-specific register headers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-regs.h

## Purpose
This header is the hardware register and bit-field contract for the Samsung JPEG codec driver. It contains no executable code; it gives the operation driver stable names for MMIO offsets, mode bits, interrupt masks, DMA address registers, image format selectors, quantization/Huffman table windows, timer fields, scaling controls, and RGB/YUV conversion coefficients across S5PC210, Exynos4x12, and Exynos3250 style JPEG blocks.

## Important APIs, Types, and Constants
The exported API is preprocessor-only. The S5P group defines legacy registers such as `S5P_JPGMOD`, `S5P_JPGINTSE`, `S5P_JPGINTST`, `S5P_JPGCOM`, raw/JPEG address registers, quantizer and Huffman table address macros, and compression/decompression mode bits. The Exynos4 group defines linear codec control, interrupt, image plane, table selection, image format, decoded size, and table-entry registers. The Exynos3250 group adds split luma/chroma plane base/stride/offset registers, source/output tiled and endian controls, decode scaling, stream-bound fields, DMA operation status, and conversion coefficient constants.

## Control Flow and State
There is no local control flow. Runtime state is represented indirectly as bits the JPEG driver writes and reads: mode selection, stream size limits, interrupt enable/status, power/clock state, timer state, DMA active state, and table selections. Because the header spans incompatible generations, call sites must choose the right register family from device data before programming hardware.

## Dependencies and Integration Points
The file is consumed by the Samsung JPEG platform driver under the same media tree. It integrates with V4L2 memory-to-memory buffer setup through DMA address offsets and format selectors, and with IRQ handling through completion/error/status masks. It depends only on normal C preprocessor semantics and kernel integer types inherited by users.

## Risks
The main risk is programming a register family on the wrong hardware generation. Many field names are similar but offsets differ, especially between S5P/Exynos4 and Exynos3250. Mask constants also encode hardware-specific reserved bits; using a broad mask when preserving unrelated fields could clear feature bits. Stream-bound and timer fields should be validated by tests around oversized JPEGs and timeout paths.

## Test Signals
Useful signals include successful encode/decode on each supported SoC variant, correct interrupt completion and error reporting, correct byte-count reporting, quantization/Huffman table loading, RGB/YUV conversion correctness, tiled and multi-plane formats on Exynos3250, and suspend/reset recovery that leaves `POWER_ON` and clock-down bits consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-jpeg/jpeg-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/Kconfig

## Purpose
This Kconfig entry exposes the Samsung S5P MFC video codec driver as `CONFIG_VIDEO_SAMSUNG_S5P_MFC`. It allows the driver to be built as a module or built-in for S5PV210/Exynos platforms, and also under `COMPILE_TEST`.

## Important APIs, Types, and Constants
The key symbol is `VIDEO_SAMSUNG_S5P_MFC`, a `tristate` named "Samsung S5P MFC Video Codec". It depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and either a supported Samsung architecture or compile-test coverage. It selects `VIDEOBUF2_DMA_CONTIG`, matching the driver's use of contiguous DMA-backed videobuf2 queues.

## Control Flow and State
Kconfig state controls whether the Makefile builds `s5p-mfc.o`. There is no runtime logic here, but the selected dependencies define what V4L2 and vb2 APIs are available to the source files.

## Dependencies and Integration Points
This item integrates the MFC driver into the media platform build. The dependency set is important because the driver registers V4L2 video devices, implements mem2mem streaming semantics, and allocates DMA-contiguous buffers for firmware, stream, and frame storage.

## Risks
The help text still says "MFC 5.1 and 6.x" although the source includes v7, v8, v10, and v12 tables. If maintainers rely on help text, supported hardware may be underdocumented. Missing dependencies on firmware loader, PM, or OF are not explicit here but may be pulled indirectly by the platform/media configuration.

## Test Signals
Build coverage should include native Exynos configs, `COMPILE_TEST`, module and built-in builds, and link checks that all objects from the Makefile resolve when this symbol is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/Makefile

## Purpose
This Makefile defines the object composition of the Samsung S5P MFC codec driver. It builds one composite object, `s5p-mfc.o`, when `CONFIG_VIDEO_SAMSUNG_S5P_MFC` is enabled.

## Important APIs, Types, and Constants
The Makefile lists the driver units: core/interrupt handling (`s5p_mfc.o`, `s5p_mfc_intr.o`), decoder and encoder front ends (`s5p_mfc_dec.o`, `s5p_mfc_enc.o`), firmware/control/PM (`s5p_mfc_ctrl.o`, `s5p_mfc_pm.o`), hardware operations (`s5p_mfc_opr.o`, `s5p_mfc_opr_v5.o`, `s5p_mfc_opr_v6.o`), and command dispatch (`s5p_mfc_cmd.o`, `s5p_mfc_cmd_v5.o`, `s5p_mfc_cmd_v6.o`).

## Control Flow and State
There is no runtime state. The build composition matters because `s5p_mfc.c` initializes operation and command tables implemented in other objects. Omitting any listed object would break version-specific hardware dispatch or V4L2 entry points.

## Dependencies and Integration Points
It integrates with the kernel kbuild system through `obj-$(CONFIG_VIDEO_SAMSUNG_S5P_MFC)`. The operation and command files correspond to register families declared in the researched headers, while decoder and encoder files provide V4L2 ioctl and vb2 queue ops used by the core probe/open paths.

## Risks
The driver supports later hardware through v6-style command dispatch and extended operation/register tables, but the Makefile only has v5 and v6 command/operation source names. That is intentional if later hardware is an extension of v6 ops, but it is a review point for new hardware support. Build tests should catch missing object references.

## Test Signals
Test with `CONFIG_VIDEO_SAMSUNG_S5P_MFC=m` and `=y`, and with compile-test enabled. Linker output should include a single composite object exporting the platform driver and resolving decoder, encoder, control, PM, command, and operation symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v10.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v10.h

## Purpose
This header layers MFC v10 register and buffer definitions on top of the v8/v7/v6 register model. It adds HEVC and VP9 codec identifiers, v10-specific clock/state/static-buffer registers, hierarchical encoding controls, and motion-estimation sizing formulas.

## Important APIs, Types, and Constants
The file exports `S5P_FIMV_MFC_CLOCK_OFF_V10`, `S5P_FIMV_MFC_STATE_V10`, decoder static-buffer registers, HEVC encoder option/register fields, hierarchical QP and bitrate layer registers, v10 context buffer sizes, firmware/CPB maxima, `MFC_VERSION_V10`, `MFC_NUM_PORTS_V10`, `S5P_FIMV_CODEC_HEVC_DEC`, `S5P_FIMV_CODEC_VP9_DEC`, `S5P_FIMV_CODEC_HEVC_ENC`, `DEC_VP9_STATIC_BUFFER_SIZE`, and `ENC_V100_*_ME_SIZE` macros.

## Control Flow and State
There is no executable flow. Runtime behavior is enabled by the core variant table in `s5p_mfc.c`, which sets `version_bit = MFC_V10_BIT`, chooses v10 buffer sizes, and points firmware to `s5p-mfc-v10.fw`. Operation code uses these constants to allocate internal memory and program codec-specific registers before host-to-RISC commands.

## Dependencies and Integration Points
It includes `regs-mfc-v8.h`, so v10 inherits the v6+ command and register layout plus v7/v8 extensions. It is consumed through `s5p_mfc_common.h` and the operation layer, and is selected by OF compatible `samsung,mfc-v10`.

## Risks
The size macros assume macro arguments represent macroblock-scale dimensions used consistently by operation code. Passing pixels where macroblocks are expected would over- or under-allocate ME buffers. HEVC and VP9 enablement also depends on firmware support and format tables; mismatches between register constants and advertised V4L2 formats can produce hard-to-debug firmware errors.

## Test Signals
Signals include v10 probe with firmware load, HEVC/VP9 decode, HEVC encode, hierarchical QP/bitrate control programming, VP9 static buffer allocation, and regression tests that v8/v6 codecs still use inherited offsets correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v12.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v12.h

## Purpose
This header defines the v12 extension of the Samsung MFC register contract. It mostly adjusts context, firmware, CPB, padding, and motion-estimation sizing limits for the v12/FSD generation while inheriting v10 registers.

## Important APIs, Types, and Constants
Exports include `MFC_CTX_BUF_SIZE_V12`, per-codec v12 context sizes, `MAX_FW_SIZE_V12`, `MAX_CPB_SIZE_V12`, `MFC_VERSION_V12`, `MFC_NUM_PORTS_V12`, `S5P_FIMV_CODEC_VP9_ENC`, `MFC_CHROMA_PAD_BYTES_V12`, `S5P_FIMV_D_ALIGN_PLANE_SIZE_V12`, and `ENC_V120_*_ME_SIZE` formulas aligned to 256 bytes.

## Control Flow and State
There is no local control flow. `s5p_mfc.c` maps OF compatible `tesla,fsd-mfc` to a v12 variant using these constants and firmware `s5p-mfc-v12.fw`. `s5p_mfc_ctrl.c` has a v12-specific behavior note: firmware is reloaded for each run because repeated initialization can fail if firmware transfer state is reused.

## Dependencies and Integration Points
The header includes `regs-mfc-v10.h`; all v6+ command semantics and v10 codec extensions remain available. It is included indirectly by `s5p_mfc_common.h`, making the version macros available to variant setup, format gating, and operation code.

## Risks
The v12 path expands CPB size to 7 MiB and changes alignment/padding assumptions. Memory pressure, CMA availability, and IOMMU behavior should be tested. The VP9 encoder codec id is declared here, but user-visible encoder support depends on the encoder format/control path outside this subset.

## Test Signals
Key signals are FSD/v12 probe, repeated open/close cycles proving firmware reload works, high-resolution decode with larger CPB, v12-aligned multi-plane frame allocation, HEVC encode ME buffer allocation, and any VP9 encode exposure tests if the encoder path advertises it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v12.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v6.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v6.h

## Purpose
This header is the primary register map for MFC v6 and the base for later v7/v8/v10/v12 definitions. It describes the v6+ host/RISC command interface, reset and firmware status registers, decoder and encoder programming windows, returned status registers, codec ids, alignment requirements, scratch/ME/TMV size formulas, and firmware/context/CPB sizes.

## Important APIs, Types, and Constants
Important groups include command registers (`S5P_FIMV_HOST2RISC_CMD_V6`, `S5P_FIMV_RISC2HOST_CMD_V6`, interrupt registers), command ids (`SYS_INIT`, `OPEN_INSTANCE`, `CH_SEQ_HEADER`, `CH_INIT_BUFS`, `CH_FRAME_START`, `CLOSE_INSTANCE`, `SLEEP`, `WAKEUP`, `FLUSH`, `NAL_ABORT`), return ids matching `s5p_mfc_irq`, context registers, error masks, decoder option/display/decode/DPB/CPB registers, encoder frame/rate-control/DPB/source/stream/H.264/MPEG4/MVC registers, codec ids for H.264 MVC, VP8, MPEG4, MPEG2, VC1, H263, and alignment/size macros.

## Control Flow and State
The constants back the v6 command flow in `s5p_mfc_cmd_v6.c`: program context/codec registers, write a host command, raise `HOST2RISC_INT`, and wait for a `RISC2HOST_CMD` return. Decoder state is represented by display and decoded status registers, DPB flags, stream size and CPB offset registers. Encoder state is represented by stream size, slice type, picture count, write pointer, and encoded source address registers.

## Dependencies and Integration Points
The file includes `linux/sizes.h` and is included by v7+ register headers. It is used by the hardware operation layer and by reset/init code in `s5p_mfc_ctrl.c`. The common header's `IS_MFCV6_PLUS()` selects this style of memory-control, reset, command, and buffer logic.

## Risks
Offsets are numerous and tightly coupled to firmware ABI. A wrong offset can corrupt adjacent hardware state rather than failing cleanly. Size formulas use dimensions in operation-specific units, so their callers must pass the expected macroblock or pixel values. The header contains FIXME comments for unknown codec slots, signaling incomplete hardware enumeration.

## Test Signals
Signals include SYS_INIT/OPEN/CLOSE/SLEEP/WAKEUP returns, header parse followed by correct `MIN_NUM_DPB` and frame dimensions, DPB allocation for all advertised decode codecs, frame done/status decoding, rate-control programming for encoders, and suspend/resume on v6+ devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v7.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v7.h

## Purpose
This header extends the v6 MFC register contract for v7 hardware. It adds VP8 encoder support, three-plane source address/stride registers, encoded-source plane return registers, VP8 encoder option registers, v7 variant limits, padding bytes, context sizes, and v7 scratch sizing formulas.

## Important APIs, Types, and Constants
Key exports are `S5P_FIMV_CODEC_VP8_ENC_V7`, source first/second/third address and stride registers, encoded source first/second/third address registers, VP8 option/filter/golden-frame/layer registers, `MAX_FW_SIZE_V7`, `MAX_CPB_SIZE_V7`, `MFC_VERSION_V7`, `MFC_NUM_PORTS_V7`, luma/chroma padding constants, context buffer sizes, `S5P_FIMV_SCRATCH_BUF_SIZE_MPEG4_DEC_V7`, and `S5P_FIMV_SCRATCH_BUF_SIZE_VP8_ENC_V7`.

## Control Flow and State
No executable flow exists. The core variant table maps `samsung,mfc-v7` and `samsung,exynos3250-mfc` to v7 buffer sizes and firmware. The command path remains v6-style, while operation code can use these additional registers when v7 capabilities are detected.

## Dependencies and Integration Points
The header includes `regs-mfc-v6.h`, so it depends on the v6 register model. It integrates with `s5p_mfc_cmd_v6.c`, which maps `S5P_MFC_CODEC_VP8_ENC` to the v7 codec id, and with encoder operation code for VP8 controls and multi-plane source programming.

## Risks
VP8 encode is only one part of the stack; V4L2 format exposure, controls, firmware, and register programming must all align. The three-plane registers also increase risk for format-specific plane ordering errors. Exynos3250 uses different clocks in the variant table, so build/runtime tests should include both v7 compatible entries.

## Test Signals
Signals include v7 firmware init, VP8 encode stream output, three-plane source formats, v7 MPEG4 decode scratch allocation, v7 padding behavior, and regression of inherited v6 decode/encode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v8.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v8.h

## Purpose
This header defines the v8 extension to the v7/v6 MFC register map. It repositions or adds decoder DPB, stride, scratch, CPB, display, decoded-frame, returned-tag, and SEI registers; it also updates selected encoder rate-control and aspect/H.264 option registers and v8 memory sizing formulas.

## Important APIs, Types, and Constants
Important exports include v8 decoder registers for minimum scratch size, first/second/third-plane DPB sizes and strides, DPB address arrays, MV buffer, scratch buffer, CPB buffer, available DPB flags, display and decoded first/second/third plane addresses, frame types, crop info, picture profile, returned tags, and MVC/SEI state. Encoder updates include fixed QP, RC config/bounds/params, padding, MV range, VBV, min scratch, aspect ratio, and H.264 options. Constants set v8 context sizes, TMV/ME/scratch formulas, 64-byte plane alignment, firmware size, CPB size, version, and port count.

## Control Flow and State
The header has no functions. It changes what state the operation layer reads after firmware commands and where it writes buffer addresses before commands. The default decoder format in `s5p_mfc_dec_init()` switches to `NV12M` for v8+ hardware, reflecting the plane-address changes declared here.

## Dependencies and Integration Points
It includes `regs-mfc-v7.h` and therefore inherits v6/v7 semantics. The core variant table maps `samsung,mfc-v8` and `samsung,exynos5433-mfc` to this version, with Exynos5433 using a three-clock setup. Decoder and encoder operation files use the v8 offsets under `IS_MFCV8_PLUS()` style predicates.

## Risks
Several v8 offsets overlap conceptually with v6 names but not addresses, so operation dispatch must select the correct register table. Plane alignment changed and v8 supports layouts different from older tiled defaults; incorrect size or stride programming can produce corrupted frames without immediate command failure.

## Test Signals
Signals include v8 probe on both compatible variants, `NV12M` decode output, three-plane decode where supported by later variants, scratch-size queries, DPB reconfiguration on resolution change, and encoder rate-control/aspect controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc-v8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc.h

## Purpose
This is the legacy MFC v5.1 register, command, status, codec-id, shared-memory, alignment, and buffer-size contract. It is the base include used by common driver code and the v5 command/operation implementation.

## Important APIs, Types, and Constants
The file defines v5 MMIO ranges, reset and host/RISC argument registers, firmware status/version, two-bank DRAM base registers, decoder and encoder buffer address registers, stream interface registers, display/decode status fields, frame-type values, buffer alignment and size constants, encoder control/rate/H.264/MPEG4 registers, codec ids, channel command ids, host-to-RISC and RISC-to-host command ids, error masks, shared-memory offsets for crop/frame tags/rate-control/DPB sizes/SEI, `MFC_OFFSET_SHIFT`, firmware/context/descriptor/shared-buffer sizes, `MFC_VERSION`, and `MFC_NUM_PORTS`.

## Control Flow and State
This header enables the v5 command flow in `s5p_mfc_cmd_v5.c`, where arguments are written to `HOST2RISC_ARG1..4` before a command is posted. Runtime state is read from stream-interface and shared-memory offsets: consumed bytes, display/decode status, decoded/display addresses, frame type, DPB size, crop information, and interrupt return codes.

## Dependencies and Integration Points
It includes `linux/kernel.h` and `linux/sizes.h`, and is included by `s5p_mfc_common.h`. The common macros `mfc_read()` and `mfc_write()` use these offsets. `s5p_mfc.c` maps compatible `samsung,mfc-v5` to two memory ports, v5 firmware, v5 buffer sizes, and clock-gating behavior.

## Risks
The v5 ABI differs materially from v6+: command arguments are explicit registers, memory uses two ports, and addresses are offset-shifted. Accidentally using v6 register or address semantics on v5 can break firmware communication. Dummy compatibility definitions for v6-only features use `-1`, so unchecked use of those macros can produce invalid MMIO offsets.

## Test Signals
Signals include v5 firmware load/init, open/close instance command returns, H.264/MPEG4/H263/VC1/MPEG2 decode, H.264/MPEG4/H263 encode, two-bank DMA allocation, shared-memory crop reporting, and error handling for warning/error code ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/regs-mfc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc.c

## Purpose
This is the core Samsung S5P/Exynos MFC platform driver. It registers decoder and encoder V4L2 mem2mem video devices, manages firmware and DMA memory, owns context scheduling, handles firmware interrupts, coordinates open/release/poll/mmap, implements watchdog recovery, and binds hardware variants from device tree.

## Important APIs, Types, and Functions
Public helper functions include `clear_work_bit()`, `set_work_bit()`, IRQ-safe variants, `s5p_mfc_get_new_ctx()`, and `s5p_mfc_cleanup_queue()`. Core runtime functions include `s5p_mfc_irq()`, `s5p_mfc_open()`, `s5p_mfc_release()`, `s5p_mfc_poll()`, `s5p_mfc_mmap()`, DMA-memory configuration helpers, `s5p_mfc_probe()`, `s5p_mfc_remove()`, suspend/resume handlers, and the platform driver declaration. Variant data defines firmware names, version bits, port count, clock names, and internal buffer sizes for v5, v6, v7, Exynos3250, v8, Exynos5433, v10, and v12/FSD.

## Control Flow
Probe maps registers, requests IRQ, configures DMA memory, initializes PM, attempts firmware load, registers V4L2 decoder/encoder devices, and initializes hardware ops/commands/register tables. Open creates a context, chooses decoder or encoder ops, sets up controls and vb2 queues, and for the first instance powers on, loads firmware, and initializes hardware. IRQ handling reads reason/error, dispatches to frame, sequence, buffer-init, stream-complete, open/close, sleep/wakeup, flush, NAL abort, or error handling, then clears interrupt flags, unlocks hardware, clocks off, wakes waiters, and schedules the next context. Release tears down queues, closes firmware instances, powers off on the last instance, and frees context state.

## State and Persistence Behavior
Persistent driver state lives in `struct s5p_mfc_dev`: context array, current context, work-bit mask, hardware lock bit, suspend bit, firmware buffer, DMA bases, watchdog counter/timer/work, PM and variant data. Per-file-handle state lives in `struct s5p_mfc_ctx`, including queues, formats, codec mode, instance id, buffer counts, DPB flags, and sequence counters. Firmware is cached after load except v12 control code reloads on each run. No filesystem state is written; firmware is read through `request_firmware()`.

## Dependencies and Integration Points
The file integrates platform devices, OF match data, V4L2 core, video_device registration, vb2 DMA-contig, reserved memory/CMA/IOMMU allocation, PM clocks, firmware control, hardware operation tables, and decoder/encoder modules. It depends on `s5p_mfc_ctrl`, `s5p_mfc_intr`, `s5p_mfc_opr`, `s5p_mfc_cmd`, and PM helpers.

## Risks
Concurrency is sensitive: `hw_lock`, `ctx_work_bits`, `irqlock`, `condlock`, and `mfc_mutex` must remain ordered correctly across IRQ, open/release, stop streaming, watchdog, and suspend. Watchdog recovery marks all contexts error and reinitializes firmware, so partial cleanup bugs can leak buffers or complete vb2 buffers twice. DMA memory selection differs between two-port, common CMA, and IOMMU modes. Remove races are mitigated by clearing `ctx->dev`, but release paths still need careful null checks.

## Test Signals
Signals include probe/remove on each compatible, simultaneous decoder/encoder contexts with round-robin scheduling, first-open firmware init and last-close poweroff, interrupt reason coverage, watchdog timeout recovery, poll readiness, mmap offset split with `DST_QUEUE_OFF_BASE`, suspend/resume while active and idle, and DMA-memory paths with reserved-memory, CMA, and IOMMU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd.c

## Purpose
This file selects the hardware command vtable for an MFC device. It is the bridge between version detection in `s5p_mfc_common.h` and the concrete v5 or v6+ host-to-RISC command implementations.

## Important APIs, Types, and Functions
The only function is `s5p_mfc_init_hw_cmds(struct s5p_mfc_dev *dev)`. It assigns `dev->mfc_cmds` to `s5p_mfc_init_hw_cmds_v6()` when `IS_MFCV6_PLUS(dev)` is true, otherwise to `s5p_mfc_init_hw_cmds_v5()`.

## Control Flow and State
The function is called from `s5p_mfc_probe()` after operation setup and before devices are registered. It mutates one field in `struct s5p_mfc_dev`; later control code calls through `dev->mfc_cmds` for sys-init, sleep, wakeup, open instance, close instance, and generic host-to-RISC commands.

## Dependencies and Integration Points
It includes common, debug, and both command-version headers. It integrates with `s5p_mfc_ctrl.c` and operation code through `struct s5p_mfc_hw_cmds`.

## Risks
The selection assumes all v6 and newer hardware uses the v6 command ABI. That is true for the included v7/v8/v10/v12 paths, but any future hardware with a changed command interface needs this dispatcher updated. A missing `dev->variant` before this call would make `IS_MFCV6_PLUS()` unsafe, but probe obtains variant data first.

## Test Signals
A simple probe test should verify `dev->mfc_cmds` is non-null for v5 and v6+ compatibles. Functional confirmation comes from successful SYS_INIT and OPEN_INSTANCE commands on both v5 and v6+ hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd.h

## Purpose
This header declares the MFC command abstraction used by control and operation code. It normalizes v5 argument-register commands and v6+ register-programmed commands behind one function-pointer table.

## Important APIs, Types, and Constants
`MAX_H2R_ARG` fixes the generic argument count at four. `struct s5p_mfc_cmd_args` carries those arguments for v5 and for generic compatibility. `struct s5p_mfc_hw_cmds` contains function pointers for `cmd_host2risc`, `sys_init_cmd`, `sleep_cmd`, `wakeup_cmd`, `open_inst_cmd`, and `close_inst_cmd`. `s5p_mfc_init_hw_cmds()` initializes the table in the device.

## Control Flow and State
There is no implementation flow, but the table defines how state transitions are requested: system init, PM sleep/wakeup, firmware instance open, and firmware instance close. Device state stores a pointer to this table in `dev->mfc_cmds`.

## Dependencies and Integration Points
It includes `s5p_mfc_common.h` for `struct s5p_mfc_dev` and `struct s5p_mfc_ctx`. The API is consumed by `s5p_mfc_ctrl.c`, `s5p_mfc_cmd.c`, and version-specific command files.

## Risks
The generic `cmd_host2risc` signature accepts argument data, but v6 ignores it because v6+ commands use specific registers. Callers must not assume the generic arguments are honored on all hardware. Missing function pointers are guarded by `s5p_mfc_hw_call()` in common code, but failures then surface as `-ENODEV`.

## Test Signals
Build tests should catch prototype drift across command implementations. Runtime tests should exercise every function pointer through init, suspend/resume, open, and close on v5 and v6+ variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v5.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v5.c

## Purpose
This file implements the host-to-RISC command table for MFC v5 hardware. v5 commands are sent by waiting for the command register to become empty, writing up to four argument registers, then writing the command id.

## Important APIs, Types, and Functions
The core helper is `s5p_mfc_cmd_host2risc_v5()`. Version-specific commands include `s5p_mfc_sys_init_cmd_v5()`, `s5p_mfc_sleep_cmd_v5()`, `s5p_mfc_wakeup_cmd_v5()`, `s5p_mfc_open_inst_cmd_v5()`, and `s5p_mfc_close_inst_cmd_v5()`. The exported initializer `s5p_mfc_init_hw_cmds_v5()` returns a static `struct s5p_mfc_hw_cmds`.

## Control Flow and State
The command helper busy-waits up to `MFC_BW_TIMEOUT` for `S5P_FIMV_HOST2RISC_CMD` to equal `S5P_FIMV_H2R_CMD_EMPTY`, writes `HOST2RISC_ARG1..4`, and posts the command. Open-instance maps `ctx->codec_mode` to v5 firmware codec ids, sets `dev->curr_ctx`, passes context offset/size, and marks `ctx->state = MFCINST_ERROR` if command posting fails. Close-instance validates the instance is not already free and posts the instance number.

## Dependencies and Integration Points
It uses v5 register constants from `regs-mfc.h`, common read/write macros, debug logging, and the command header. `s5p_mfc_ctrl.c` waits for the corresponding interrupt returns after this layer posts commands.

## Risks
The busy-wait can fail if firmware or hardware leaves the command register non-empty. Codec mapping defaults to `S5P_FIMV_CODEC_NONE`, so unsupported codec requests may reach firmware unless earlier format validation prevents them. Context offsets and sizes must be v5 bank-relative, not v6 DMA addresses.

## Test Signals
Signals include command timeout handling, SYS_INIT after firmware load, sleep/wakeup, open/close for every v5-supported codec, and proper error state if open/close command posting fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v5.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v5.h

## Purpose
This header exposes the v5 command vtable initializer to the command dispatcher.

## Important APIs, Types, and Functions
It declares `const struct s5p_mfc_hw_cmds *s5p_mfc_init_hw_cmds_v5(void);` and includes `s5p_mfc_common.h` for the command table type.

## Control Flow and State
There is no local control flow or stored state. Calling the initializer returns the static command table implemented in `s5p_mfc_cmd_v5.c`.

## Dependencies and Integration Points
It is included by `s5p_mfc_cmd.c`, which chooses v5 commands for non-v6-plus devices. The returned table is stored in `dev->mfc_cmds`.

## Risks
The include guard comment names `S5P_MFC_CMD_H_` rather than its own guard, which is harmless but mildly confusing. Prototype drift between this header and the implementation would break builds.

## Test Signals
Compile coverage with v5 support enabled validates the declaration. Runtime v5 probe and SYS_INIT validates that the dispatcher can call the returned table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v6.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v6.c

## Purpose
This file implements the command table for MFC v6 and newer hardware. Unlike v5, command parameters are programmed into dedicated registers by operation code or command-specific helpers, then a host command and interrupt bit are written.

## Important APIs, Types, and Functions
Key functions are `s5p_mfc_cmd_host2risc_v6()`, `s5p_mfc_sys_init_cmd_v6()`, `s5p_mfc_sleep_cmd_v6()`, `s5p_mfc_wakeup_cmd_v6()`, `s5p_mfc_open_inst_cmd_v6()`, `s5p_mfc_close_inst_cmd_v6()`, the compatibility wrapper `s5p_mfc_cmd_host2risc_v6_args()`, and exported `s5p_mfc_init_hw_cmds_v6()`.

## Control Flow and State
The generic helper clears `RISC2HOST_CMD_V6`, writes `HOST2RISC_CMD_V6`, and raises `HOST2RISC_INT_V6`. SYS_INIT allocates a device context buffer, writes its DMA address and size, and posts the sys-init command. Open-instance maps `ctx->codec_mode` to v6/v7/v10 codec ids, sets `dev->curr_ctx`, writes codec type, context DMA address, context size, and CRC control, then posts OPEN_INSTANCE. Close-instance writes `INSTANCE_ID_V6` when the context is not free and posts CLOSE_INSTANCE.

## Dependencies and Integration Points
It uses common macros, interrupt definitions, operation helpers for context allocation, and codec constants from v6+ register headers. `s5p_mfc_ctrl.c` handles waits and resource cleanup around the command calls.

## Risks
The command helper does not poll for an empty command register like v5; correctness depends on higher-level `hw_lock` serialization. Unsupported codec modes map to `S5P_FIMV_CODEC_NONE_V6`, so format/control validation must prevent invalid firmware opens. HEVC and VP9 mappings depend on v10+ constants being included through the common header.

## Test Signals
Signals include v6+ SYS_INIT context allocation, open/close for all advertised decode and encode codecs, sleep/wakeup across suspend/resume, and command serialization under concurrent contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v6.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v6.h

## Purpose
This header exposes the v6+ command vtable initializer to the command dispatcher.

## Important APIs, Types, and Functions
It declares `const struct s5p_mfc_hw_cmds *s5p_mfc_init_hw_cmds_v6(void);` and includes `s5p_mfc_common.h`.

## Control Flow and State
There is no executable flow. The initializer returns the static table implemented in `s5p_mfc_cmd_v6.c`, which is stored in `dev->mfc_cmds` for v6 and later variants.

## Dependencies and Integration Points
It is included by `s5p_mfc_cmd.c`. Downstream calls are made from firmware control, PM, and instance lifecycle paths.

## Risks
The header covers all v6+ hardware, so any future command ABI split must not be hidden behind this single initializer. The include guard closing comment references `S5P_MFC_CMD_H_`, which is harmless but imprecise.

## Test Signals
Compile coverage and runtime SYS_INIT/OPEN_INSTANCE on v6+ variants validate this declaration and dispatch path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_cmd_v6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_common.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_common.h

## Purpose
This is the central shared contract for the MFC driver. It defines codec ids, interrupt ids, instance and queue states, buffer wrappers, PM and variant data, device and context state structures, encoder parameter structures, pixel format descriptors, control descriptors, hardware-call helpers, version predicates, and common helper prototypes.

## Important APIs, Types, and Constants
Major types include `struct s5p_mfc_dev`, `struct s5p_mfc_ctx`, `struct s5p_mfc_buf`, `struct s5p_mfc_pm`, `struct s5p_mfc_variant`, `struct s5p_mfc_priv_buf`, per-version buffer-size structs, `struct s5p_mfc_enc_params` and codec-specific parameter structs, `struct s5p_mfc_codec_ops`, `struct s5p_mfc_fmt`, and `struct mfc_control`. Important macros include `mfc_read`, `mfc_write`, `s5p_mfc_hw_call`, `file_to_ctx`, `ctrl_to_ctx`, version predicates, version bit masks, limits such as `MFC_NUM_CONTEXTS`, `MFC_MAX_BUFFERS`, `MFC_INT_TIMEOUT`, and interrupt/code constants.

## Control Flow and State
There is no executable implementation except small inline accessors/macros. It defines the state machine used throughout the driver: `MFCINST_INIT`, `GOT_INST`, `HEAD_PARSED`, `BUFS_SET`, `RUNNING`, `FINISHING`, `FINISHED`, `RETURN_INST`, `ERROR`, `ABORT`, `FLUSH`, and resolution-change states. It also defines per-queue state transitions from free to requested, queried, and mmaped.

## Dependencies and Integration Points
It includes V4L2, vb2, platform-device, register headers, and DMA-contig definitions. Every MFC source file in this subset relies on these structures. Hardware operation and command tables attach to `struct s5p_mfc_dev`, while decoder/encoder ioctl and queue code attach to `struct s5p_mfc_ctx`.

## Risks
This header has high blast radius. Structure field changes can break locking, vb2 callback assumptions, firmware ABI programming, and PM paths. The `s5p_mfc_hw_call()` macro derives a fallback type from `f->op(args)`, so it depends on valid function-pointer expressions at compile time. Version predicates assume `dev->variant` is valid.

## Test Signals
Build coverage across all MFC objects is essential. Runtime signals include stable context lifecycle, state-machine transitions under decode/encode/EOS/resolution-change, correct version-gated format exposure, control propagation into context fields, and no lockdep issues around `mfc_mutex`, `irqlock`, and `condlock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_ctrl.c

## Purpose
This file manages firmware memory, firmware loading, hardware reset/init/deinit, sleep/wakeup, and firmware instance open/close. It is the main lifecycle control layer between the platform driver and the version-specific command/operation tables.

## Important APIs, Types, and Functions
Exports include `s5p_mfc_alloc_firmware()`, `s5p_mfc_load_firmware()`, `s5p_mfc_release_firmware()`, `s5p_mfc_reset()`, `s5p_mfc_init_hw()`, `s5p_mfc_deinit_hw()`, `s5p_mfc_sleep()`, `s5p_mfc_wakeup()`, `s5p_mfc_open_mfc_inst()`, and `s5p_mfc_close_mfc_inst()`. Internal helpers include `s5p_mfc_bus_reset()`, `s5p_mfc_init_memctrl()`, `s5p_mfc_clear_cmds()`, `s5p_mfc_v8_wait_wakeup()`, and `s5p_mfc_wait_wakeup()`.

## Control Flow
Firmware allocation reserves an internal private buffer sized by the hardware variant. Firmware load tries newer firmware slots first, copies into firmware memory, and caches success except v12 reloads for each run. Init resets hardware, programs memory base addresses, clears command state, releases RISC reset, waits for firmware transfer, posts SYS_INIT, waits for SYS_INIT return, checks interrupt error/type, reads firmware version, and clocks off. Sleep/wakeup post PM commands and wait for returns. Open-instance allocates instance and decoder temp buffers, sets the work bit, runs hardware, waits for OPEN_INSTANCE return, and cleans resources on failure. Close-instance posts close, waits, releases codec/instance/decoder buffers, and marks the context free.

## State and Persistence Behavior
State changes affect firmware buffer fields, `dev->fw_get_done`, `dev->fw_ver`, `dev->risc_on`, device/context private buffers, `ctx->state`, `ctx->inst_no`, and command wait conditions. Firmware bytes are copied from `/lib/firmware` or built-in firmware into DMA memory.

## Dependencies and Integration Points
It depends on firmware loader APIs, jiffies/timeouts, MFC PM clock helpers, interrupt wait helpers, private buffer allocation in the operation layer, command tables, and register constants. It is called from probe/open/release/watchdog/suspend/resume.

## Risks
Reset/init sequencing is hardware-sensitive. Missing clock-off paths on error can leak PM refs. v12's forced firmware reload is an important special case; removing it can break second initialization. Open-instance cleanup must release decoder temp buffers and instance buffers in the right order. Wait timeouts can leave hardware locked unless callers clear work bits.

## Test Signals
Signals include firmware missing/oversized errors, init timeout paths, successful firmware version read, repeated v12 open/close, suspend/resume sleep/wakeup, watchdog deinit/reinit, and allocation failure injection for firmware, device context, instance, and decoder temp buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_ctrl.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_ctrl.h

## Purpose
This header declares the MFC firmware, hardware lifecycle, PM, reset, and instance lifecycle APIs implemented by `s5p_mfc_ctrl.c`.

## Important APIs, Types, and Functions
The declarations cover firmware allocation/release/load, hardware init/deinit, sleep/wakeup, reset, open MFC instance, and close MFC instance. All functions operate on `struct s5p_mfc_dev` and, for instance lifecycle, `struct s5p_mfc_ctx`.

## Control Flow and State
There is no local flow. The functions declared here drive transitions at the device level and context level: firmware memory available, firmware loaded, hardware initialized, hardware sleeping/awake, firmware instance opened, and firmware instance closed.

## Dependencies and Integration Points
It includes `s5p_mfc_common.h` for device/context types and is used by core, PM, watchdog, probe/open/release, and possibly operation paths.

## Risks
The API has no explicit locking annotations, but callers must hold or coordinate with `mfc_mutex`, `hw_lock`, clocks, and wait queues depending on context. Misuse can race firmware init with open/release or suspend.

## Test Signals
Compile checks validate prototypes. Runtime coverage should call each API through normal open/close, first-open init, last-close deinit, suspend/resume, and watchdog recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_debug.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_debug.h

## Purpose
This header provides local logging macros for the MFC driver. It centralizes debug, error, rate-limited error, and info logging with function and line metadata.

## Important APIs, Types, and Constants
`mfc_debug_level` is an external integer controlled by the module parameter in `s5p_mfc.c`. `mfc_debug(level, fmt, ...)` prints `KERN_DEBUG` messages when the configured level is high enough. `mfc_debug_enter()` and `mfc_debug_leave()` are shorthand for level-5 tracing. `mfc_err()`, `mfc_err_limited()`, and `mfc_info()` print error or info messages.

## Control Flow and State
The only state dependency is `mfc_debug_level`. The file defines `DEBUG`, so debug macro code is always compiled in for this driver, with runtime filtering by level.

## Dependencies and Integration Points
It relies on kernel `printk` and `printk_ratelimited` symbols through normal kernel headers included by users. Nearly every MFC source file includes this header for diagnostics.

## Risks
Always compiling debug logging can add code size and make excessive logs possible if the debug module parameter is raised. `mfc_err()` is not rate-limited, so repeated hardware errors can flood logs; callers should use `mfc_err_limited()` in noisy paths, as decode DQBUF does.

## Test Signals
Signals include module parameter behavior, debug-level filtering, function/line metadata in logs, and rate limiting during repeated error calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_dec.c

## Purpose
This file implements the decoder-facing V4L2 ioctl, control, and vb2 queue behavior for the Samsung MFC driver. It maps user-visible compressed and raw formats to firmware codec modes, controls decoder setup, manages OUTPUT/CAPTURE buffer requests, handles EOS commands and source-change events, and feeds queued buffers into the core scheduler.

## Important APIs, Types, and Functions
Static data includes the decoder `formats[]` table and decoder controls. Important helpers are `find_format()`, `s5p_mfc_ctx_ready()`, V4L2 ioctl handlers for querycap, enum/g/s/try format, reqbufs, querybuf, qbuf, dqbuf, expbuf, streamon/off, selection, decoder command, event subscribe, decoder control get/set, and vb2 ops: `s5p_mfc_queue_setup()`, `s5p_mfc_buf_init()`, `s5p_mfc_start_streaming()`, `s5p_mfc_stop_streaming()`, and `s5p_mfc_buf_queue()`. Exported accessors return decoder codec ops, queue ops, ioctl ops, set up/delete controls, and initialize default formats.

## Control Flow
The decode path starts with `S_FMT` on OUTPUT selecting compressed codec and setting `MFCINST_INIT`. OUTPUT `REQBUFS` opens a firmware instance. Header parse occurs when a source buffer is queued and the context is ready. After `SEQ_DONE`, CAPTURE format and min buffers become available. CAPTURE `REQBUFS` allocates DPB/codec buffers, queues init buffers, and waits for `INIT_BUFFERS_RET`. Streaming and buffer queue callbacks add buffers to internal queues, set work bits when `s5p_mfc_ctx_ready()` is true, and call `try_run`. `V4L2_DEC_CMD_STOP` marks EOS on the last source buffer or enters finishing state when the source queue is empty. DQBUF emits `V4L2_EVENT_EOS` when the finished EOS capture buffer is dequeued.

## State and Persistence Behavior
The file mutates `ctx->src_fmt`, `dst_fmt`, `codec_mode`, `dec_src_buf_size`, `state`, queue states, source/destination buffer arrays, queue counts, DPB counts, `dec_dst_flag`, display-delay controls, loop-filter and slice-interface flags, and default format selections. It uses vb2 queue state and V4L2 control state but writes no persistent storage.

## Dependencies and Integration Points
It integrates with V4L2 ioctl/event/control APIs, vb2 DMA-contig, core scheduler work bits, firmware control (`s5p_mfc_open_mfc_inst()`), hardware operations (`alloc_codec_buffers`, `release_codec_buffers`, `try_run`), PM clocks, and interrupt wait helpers.

## Risks
State validation is strict and easy to regress: CAPTURE buffers are valid only after header parse, OUTPUT buffers only after format init, and only MMAP memory is accepted for decoder queues. Resolution-change flow depends on core IRQ state transitions. Stop-streaming can wait for a frame interrupt while holding/releasing locks, so lock ordering is important. Format version masks must match firmware capabilities.

## Test Signals
Signals include format enumeration per hardware version, invalid format rejection, header-parse wait before CAPTURE format/min-buffers, buffer count clamping, DPB allocation failure cleanup, EOS event delivery, resolution-change source-change events, streamoff while running, and decode for H.264, MPEG2, MPEG4/H263, VC1, VP8, HEVC, and VP9 where version-gated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_dec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_dec.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_dec.h

## Purpose
This header declares the decoder module's integration points for the MFC core open path.

## Important APIs, Types, and Functions
It declares `get_dec_codec_ops()`, `get_dec_queue_ops()`, `get_dec_v4l2_ioctl_ops()`, `s5p_mfc_dec_ctrls_setup()`, `s5p_mfc_dec_ctrls_delete()`, and `s5p_mfc_dec_init()`.

## Control Flow and State
There is no implementation flow. The core calls these functions when opening a decoder video node: initialize default decode formats, attach decoder controls, and install decoder vb2 and ioctl operations.

## Dependencies and Integration Points
The declarations rely on types from `s5p_mfc_common.h`, included by users before this header in the current source arrangement. It connects `s5p_mfc.c` to `s5p_mfc_dec.c`.

## Risks
Because this header does not include `s5p_mfc_common.h` itself, it assumes include ordering provides `struct s5p_mfc_ctx`, `struct s5p_mfc_codec_ops`, `struct vb2_ops`, and `struct v4l2_ioctl_ops`. That is true in current users but could be fragile for new include sites.

## Test Signals
Compile coverage validates include ordering. Runtime decoder open should call init/control setup successfully and use returned ioctl/queue ops for all decode operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_dec.h -->
