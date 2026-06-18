# Research: subset-b-004138

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu-enc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu-enc.c

## Purpose
Implements the V4L2 mem2mem encoder frontend for the Chips&Media Wave5 VPU. It exposes HEVC/H.264 capture formats, raw YUV output formats, V4L2 controls, vb2 queue handling, encoder stream state transitions, and the mem2mem `device_run` callback that submits one encode job to firmware.

## Important APIs, Types, and Functions
Key exported integration points are `wave5_vpu_enc_register_device()` and `wave5_vpu_enc_unregister_device()`, called by the platform driver. `wave5_vpu_open_enc()` allocates `struct vpu_instance`, initializes V4L2 controls, formats, completion, kfifo, mem2mem context, SRAM, and instance IDs. `wave5_vpu_enc_release()` delegates cleanup to common release logic. Runtime path functions include `wave5_vpu_enc_start_streaming()`, `wave5_vpu_enc_stop_streaming()`, `wave5_vpu_enc_device_run()`, `start_encode()`, and `wave5_vpu_enc_finish_encode()`. Format/ioctl handlers validate stepwise dimensions and maintain `src_fmt`, `dst_fmt`, crop/conformance window, colorimetry, and frame rate. The long `wave5_vpu_enc_s_ctrl()` maps V4L2 MPEG controls into `inst->enc_param` and encoder flags.

## Control Flow
Open creates an encoder instance and default NV12-to-HEVC format. OUTPUT stream-on opens the firmware instance with `wave5_set_enc_openparam()`. Once both queues stream, sequence init is issued, `wave5_vpu_wait_interrupt()` waits for firmware completion, sequence info sets minimum source/FBC buffer counts, compressed frame buffers are allocated and registered, and state advances to `PIC_RUN`. Each mem2mem job calls `start_encode()`, maps source/destination DMA addresses into `struct enc_param`, removes the source buffer from the ready queue by index, and lets the IRQ completion path finish it after firmware reports `enc_src_idx`. `wave5_vpu_enc_finish_encode()` retrieves firmware output, finishes the source vb2 buffer, removes and completes the destination buffer, marks frame type flags, handles firmware EOS via `RECON_IDX_FLAG_ENC_END`, queues `V4L2_EVENT_EOS`, and calls `v4l2_m2m_job_finish()`.

## State and Persistence
State is per open file in `struct vpu_instance`: V4L2 formats, crop window, colorimetry, frame rate, rate-control values, codec standard, vb2 sequence counters, FBC frame buffers, timestamp, and `VPU_INST_STATE_*`. Persistent device state is shared through `struct vpu_device` and firmware-side `enc_info`. No on-disk state is written.

## Dependencies and Integration Points
Depends on V4L2 mem2mem, vb2 DMA-contig, V4L2 controls/events, Wave5 helper APIs (`wave5_vpu_enc_*`), common helper code from `wave5-helper.h`, and runtime PM. It integrates with the platform driver through video registration and with interrupt handling through `inst->ops->finish_process`.

## Risks
State transitions are enforced but failures after partial open/sequence init must return queued buffers correctly. Source buffer completion relies on firmware returning a valid `enc_src_idx`; stale or invalid indices can leave buffers active. FBC allocation failure cleanup calls decoder-named reset helpers, which is intentional shared cleanup but worth regression coverage. Runtime PM return values from `pm_runtime_resume_and_get()` are not consistently checked. Control mappings are broad and can silently preserve incompatible combinations until firmware validation.

## Test Signals
Exercise `v4l2-compliance` mem2mem ioctls, HEVC/H.264 encode smoke tests with NV12/NV21/NV16 multi-plane and single-plane inputs, EOS drain with and without final source buffers, streamoff during active jobs, format changes before queue allocation, crop bounds, profile/level/QP/rate-control controls, and error injection for firmware queueing failure and missing destination buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu-enc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu.c

## Purpose
Platform driver for Wave5 VPU devices. It binds device-tree compatible hardware, maps registers, configures DMA, clocks, resets, SRAM, firmware, runtime PM, IRQ or polling-based completion, V4L2 device registration, and encoder/decoder video node registration.

## Important APIs, Types, and Functions
`wave5_vpu_probe()` is the main bring-up routine; `wave5_vpu_remove()` tears the device down. `wave5_vpu_wait_interrupt()` is shared by sequence setup paths. IRQ handling is split between hard IRQ `wave5_vpu_irq()`, threaded IRQ `wave5_vpu_irq_thread()`, and the fallback polling path `wave5_vpu_timer_callback()`, `wave5_vpu_irq_work_fn()`, and `irq_thread()`. `wave5_vpu_load_firmware()` requests firmware and initializes the VPU. PM callbacks call `wave5_vpu_sleep_wake()` and clock operations.

## Control Flow
Probe validates match data, sets a 32-bit DMA mask, allocates `struct vpu_device`, maps the register region, deasserts reset, enables clocks, obtains optional SRAM, initializes VDI/common memory, sets up IRQ or polling workers, registers a V4L2 device, registers decoder and encoder nodes depending on match flags, loads firmware, enables runtime PM, then sleeps the VPU. IRQ service reads interrupt reason and per-instance done bits, clears hardware interrupt registers, records picture completion into each instance kfifo, completes sequence waits, and schedules threaded processing. The thread drains per-instance IRQ status and calls `inst->ops->finish_process()`.

## State and Persistence
`struct vpu_device` persists for the platform device lifetime and owns locks, instance list, register base, common memory, SRAM metadata, clock/reset handles, IRQ or polling worker state, V4L2 device, and video devices. Per-instance completions and FIFOs are updated from IRQ context. No persistent storage is used outside requested firmware loading.

## Dependencies and Integration Points
Uses Linux platform, OF match data, firmware loader, reset/clock/runtime PM APIs, gen_pool SRAM, V4L2 registration, threaded IRQs, hrtimers, kthread workers, and Wave5 VDI/backend functions. It expects firmware `cnm/wave521c_k3_codec_fw.bin` for `ti,j721s2-wave521c`.

## Risks
The IRQ handler scans all instances and depends on firmware instance bitmaps matching `inst->id`. Fallback polling is more complex and must avoid worker/thread leaks on probe errors. Runtime resume calls sleep/wake before enabling clocks, which should be validated against hardware expectations. Remove unregisters both encoder and decoder unconditionally, so disabled capability combinations rely on unregister helpers tolerating absent devices.

## Test Signals
Probe/remove on device-tree matched systems, missing firmware path, no-IRQ fallback polling, suspend/resume and runtime autosuspend, concurrent encoder/decoder instances, interrupt storms with multiple instance IDs, reset/clock failure injection, and `v4l2-compliance` node visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu.h

## Purpose
Small driver-facing header for Wave5 V4L2 frontend code. It defines buffer wrappers, format metadata, helpers for converting file/control handles to `struct vpu_instance`, device registration prototypes, and the shared "both queues streaming" predicate.

## Important APIs, Types, and Functions
Defines `struct vpu_src_buffer`, `struct vpu_dst_buffer`, `enum vpu_fmt_type`, and `struct vpu_format`. Inline helpers include `wave5_to_vpu_inst()`, `file_to_vpu_inst()`, `wave5_ctrl_to_vpu_inst()`, `wave5_to_vpu_src_buf()`, `wave5_to_vpu_dst_buf()`, and `wave5_vpu_both_queues_are_streaming()`. It declares encoder/decoder register/unregister functions and `wave5_vpu_wait_interrupt()`.

## Control Flow
No executable control flow beyond inline conversions and queue state checks. The queue predicate obtains capture/output queues from the mem2mem context and returns true only if both vb2 queues are streaming.

## State and Persistence
The header defines wrappers around V4L2 mem2mem buffers with flags such as `consumed` and `display`, but it does not allocate or persist state itself.

## Dependencies and Integration Points
Includes V4L2 controls, ioctl, events, file handles, vb2 V4L2, DMA-contig, vmalloc, `wave5-vpuconfig.h`, and `wave5-vpuapi.h`. It is the shared include for Wave5 encoder, decoder, and platform/frontend helpers.

## Risks
Container conversions assume exact embedding of fields in `struct vpu_instance` and buffer structs. `wave5_vpu_both_queues_are_streaming()` assumes a valid initialized mem2mem context.

## Test Signals
Compile coverage across encoder and decoder builds, open/close path tests that exercise handle conversion, and stream-on ordering tests for the both-queues predicate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuapi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuapi.c

## Purpose
Implements the higher-level Wave5 API used by V4L2 encoder/decoder frontends. It serializes firmware/backend calls, validates parameters, tracks codec instance state, manages firmware open/close, sequence init, bitstream pointers, frame-buffer registration, encode/decode command submission, output result conversion, and command-style state updates.

## Important APIs, Types, and Functions
Initialization functions include `wave5_vpu_init_with_bitcode()`, `wave5_initialize_vpu()`, and `wave5_vpu_get_version_info()`. Decoder APIs cover `wave5_vpu_dec_open()`, `wave5_vpu_dec_close()`, sequence init/complete, frame-buffer registration, bitstream buffer query/update, decode start, rd pointer management, output info, display flag management, reset framebuffer, and `wave5_vpu_dec_give_command()`. Encoder APIs cover `wave5_vpu_enc_open()`, `wave5_vpu_enc_close()`, frame-buffer registration, parameter checking, `wave5_vpu_enc_start_one_frame()`, output info, `wave5_vpu_enc_give_command()`, and sequence init/complete.

## Control Flow
All hardware/firmware calls are wrapped by `vpu_dev->hw_lock`. Firmware init resets the VPU unless already initialized, in which case it reinitializes and returns busy. Decoder open validates bitstream alignment and initializes circular stream pointers. Decoder close loops `dec_finish_seq`, handles still-running firmware by collecting output, then frees work/task/auxiliary DMA. Encoder open validates open parameters and builds firmware state. Encoder stream submission stores PTS by source index and calls `wave5_vpu_encode()`. Encoder output reads firmware result and restores PTS from the map. Close loops `enc_finish_seq` until firmware exits or retry limit expires, then frees work, task, sub-sampled, MV, and FBC buffers.

## State and Persistence
This file mutates `inst->codec_info->dec_info` and `enc_info`: open parameters, stream pointers, initial sequence info, display flags, registered buffer counts, stride, PTS map, queue counters, and DMA buffer handles. It also gates global VPU state through `vpu_device->hw_lock`. No disk persistence exists.

## Dependencies and Integration Points
Depends on backend functions declared in `wave5.h`, register definitions, VDI DMA helpers, runtime PM, and Wave5 error/config constants. It is the bridge between V4L2-facing frontend files and firmware command implementation.

## Risks
Several close error paths call `pm_runtime_resume_and_get()` where a put was likely intended, making PM reference leaks a review target. `pts_map` indexes by `src_idx` and assumes firmware returns indices within its fixed size. Decoder circular buffer arithmetic must preserve one-byte empty space and reject overlap. Retry loops depend on firmware fail reasons being precise. `wave5_vpu_dec_reset_framebuffer()` returning `-EINVAL` for empty slots is used as a loop terminator in callers.

## Test Signals
Unit-like fault injection around mutex interruption, firmware busy retries, close while frames are pending, circular bitstream wraparound, invalid alignment/size parameters, PTS propagation across reordered jobs, sequence-change decode streams, and PM refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuapi.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuapi.h

## Purpose
Central Wave5 API and state header. It defines product IDs, codec standards, instance states, firmware constants, codec command enums, frame-buffer and geometry structures, decoder/encoder parameter/result structures, device/instance state structures, and prototypes for VDI and API operations.

## Important APIs, Types, and Functions
Important types include `struct vpu_device`, `struct vpu_instance`, `struct dec_info`, `struct enc_info`, `struct frame_buffer`, `struct dec_open_param`, `struct dec_initial_info`, `struct dec_output_info`, `struct enc_wave_param`, `struct enc_open_param`, `struct enc_param`, and `struct enc_output_info`. Constants define framebuffer limits, work-buffer sizing formulas, bitstream buffer rules, profile/level values, reset modes, interrupts, frame maps, queue status, EOS sentinel indices, and codec commands.

## Control Flow
The header itself has no runtime flow but defines the state machine used by frontends: `NONE`, `OPEN`, `INIT_SEQ`, `PIC_RUN`, and `STOP`. API prototypes split flow into init/version, decoder open/sequence/register/decode/output/close, and encoder open/sequence/register/encode/output/close.

## State and Persistence
`struct vpu_device` owns persistent platform lifetime state: V4L2 devices, mem2mem devices, instance list, locks, product data, common memory, SRAM, register base, clocks, reset, IRQ/polling state, and ID allocator. `struct vpu_instance` owns per-open state: formats, controls, completion, kfifo, codec info union pointer, frame buffers, bitstream buffer, EOS/retry flags, crop, frame rate, rate-control and encoder parameters.

## Dependencies and Integration Points
Includes kfifo, IDA, genalloc, V4L2 device/mem2mem/controls, Wave5 VDI, config, and error headers. It is consumed by all Wave5 frontend and backend implementation files.

## Risks
ABI-like coupling is high: changing structures affects many C files. Fixed array sizes (`WAVE5_MAX_FBS`, `MAX_REG_FRAME`, `pts_map[32]`) must match firmware and V4L2 buffer assumptions. The header contains a duplicated `vdb_register` field in `struct vpu_device`, which is a compile-time or maintenance concern depending on the exact source baseline. Bitfield packing is compiler-defined but confined to kernel C usage.

## Test Signals
Build all Wave5 objects with sparse/W=1, run structure-user compile coverage for encoder/decoder, validate max buffer counts, exercise all state transitions, and verify firmware result indices never exceed fixed arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuapi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuconfig.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuconfig.h

## Purpose
Defines Wave5 product codes, supported product macro, instance limits, default/min/max dimensions, timeouts, command queue depth, common memory sizes, work-buffer sizes, remap sizes, and AXI IDs.

## Important APIs, Types, and Functions
Key macros include `PRODUCT_CODE_W_SERIES()`, product codes such as `WAVE521C_CODE`, `MAX_NUM_INSTANCE`, encoder/decoder picture dimension limits, `VPU_ENC_TIMEOUT`, `VPU_DEC_TIMEOUT`, `WAVE521_COMMAND_QUEUE_DEPTH`, and common memory size formulas.

## Control Flow
No runtime control flow. The values constrain validation and allocation in platform/API/frontend code.

## State and Persistence
No state. These constants influence memory allocation sizes, firmware timeout behavior, and V4L2 frame-size negotiation.

## Dependencies and Integration Points
Included by `wave5-vpu.h`, `wave5-vpuapi.h`, platform code, and frontend format handling. Hardware backend code depends on product and memory constants.

## Risks
Incorrect size constants can cause firmware memory corruption or under-allocation. Dimension and step constants directly affect userspace-advertised capabilities. The `PRODUCT_CODE_W_SERIES()` statement expression is GCC-specific, which is acceptable in kernel code.

## Test Signals
Compile on supported configs, validate advertised frame sizes with `v4l2-compliance`, stress max resolution encode/decode allocations, and run firmware initialization on each product code variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuconfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuerror.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuerror.h

## Purpose
Collects Wave5 firmware/system, command queue, decoder syntax/spec, warning, encoder warning, and debug reason bit values used to interpret firmware fail and warning registers.

## Important APIs, Types, and Functions
Defines common system errors such as `WAVE5_SYSERR_QUEUEING_FAIL`, `WAVE5_SYSERR_VPU_STILL_RUNNING`, watchdog/VCPU timeout, and fatal hangup masks. It enumerates HEVC and AVC SPS/PPS/slice/spec/etc error codes plus warning masks. It also defines `WAVE5_ETCWARN_FORCED_SPLIT_BY_CU8X8` and debug reason codes.

## Control Flow
No executable flow. Callers compare firmware fail reasons against these macros to decide whether to retry, drain, return `-EINVAL`, or time out.

## State and Persistence
No state. Values are transient interpretations of firmware result registers and output info fields.

## Dependencies and Integration Points
Included by `wave5-vpuapi.h`, which is used across frontend/API/backend code. Encoder and decoder completion paths surface these values in debug or warning logs.

## Risks
Mislabeling constants leads to wrong retry/error handling. The fatal mask overlaps broad high bits and should be used with care. Large sets of parser-specific values are hard to test without targeted bitstreams.

## Test Signals
Firmware error injection, malformed HEVC/AVC decode streams, queue-full/queueing-fail encode scenarios, close while VPU is still running, and log verification that fail reasons are surfaced accurately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpuerror.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5.h

## Purpose
Declares low-level Wave5 backend operations and hardware-facing constants used by the higher-level API. It bridges frontend/API code to register/firmware command implementation.

## Important APIs, Types, and Functions
Defines sub-sampled buffer sizing macros, bitstream option bits, endian configuration constants, WTL constants, rotation/mirror mode encodings, and prototypes for VPU init, sleep/wake, reset, version, decoder commands, interrupt clear, read/write pointer operations, encoder build/init/register/encode/result/finish/check operations.

## Control Flow
No implementation here. The declared backend calls form the firmware command sequence used by `wave5-vpuapi.c`: initialize, build instance parameters, issue sequence init, register framebuffers, submit pictures, collect results, and finish sequences.

## State and Persistence
No state. It defines constants that affect how backend code programs hardware registers and firmware command memory.

## Dependencies and Integration Points
Depends on `struct vpu_device`, `struct vpu_instance`, and codec structs from `wave5-vpuapi.h`. Called by platform initialization and encoder/decoder API wrappers.

## Risks
Backend prototypes are central coupling points; signature changes ripple widely. Hard-coded big-endian register write constants are a hardware assumption that should be validated on any new integration. Rotation/mirror constants must match firmware PRP encodings.

## Test Signals
Compile/link coverage with backend implementation, firmware init/sleep/wake/reset smoke tests, encode/decode command submission, bitstream EOS behavior, and rotation/mirror encode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/Kconfig

## Purpose
Adds the Kconfig option for the Imagination E5010 JPEG encoder V4L2 mem2mem driver.

## Important APIs, Types, and Functions
Defines `CONFIG_VIDEO_E5010_JPEG_ENC` as a tristate with prompt "Imagination E5010 JPEG Encoder Driver". It depends on `VIDEO_DEV` and `ARCH_K3 || COMPILE_TEST`, and selects `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, and `V4L2_JPEG_HELPER`.

## Control Flow
No runtime flow. Build-system selection controls whether the E5010 module is compiled.

## State and Persistence
No runtime state. The selected config persists in kernel `.config`.

## Dependencies and Integration Points
Integrates the Imagination platform directory into the media Kconfig tree and ensures vb2/mem2mem/JPEG helper dependencies are enabled.

## Risks
Missing dependency selections cause link failures. The hardware dependency is K3-oriented but compile-testable. The help text states module name `e5010_jpeg_enc`, matching the Makefile object.

## Test Signals
`make menuconfig` visibility, `allyesconfig`/`allmodconfig`/`COMPILE_TEST` builds, and module load on K3 device-tree systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/Makefile

## Purpose
Builds the Imagination E5010 JPEG encoder module from its core driver and hardware helper objects.

## Important APIs, Types, and Functions
Defines `e5010_jpeg_enc-objs := e5010-jpeg-enc-hw.o e5010-jpeg-enc.o` and adds the module through `obj-$(CONFIG_VIDEO_E5010_JPEG_ENC) += e5010_jpeg_enc.o`.

## Control Flow
No runtime flow. Kbuild links the hardware abstraction and V4L2 driver implementation into one module when the Kconfig symbol is enabled.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Depends on the Kconfig symbol and Kbuild media platform traversal. The object order places hardware helpers before main driver in the module object list, though both are linked together.

## Risks
Adding new source files without updating this Makefile causes unresolved references. Renaming the config or objects breaks module builds.

## Test Signals
Module build with `CONFIG_VIDEO_E5010_JPEG_ENC=m` and built-in build with `=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-core-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-core-regs.h

## Purpose
Register map for the Imagination/Jasper E5010 JPEG encoder core. It defines offsets, masks, and shifts for core identity, interrupts, clock/reset, input control, MMU control, image size, buffer base addresses, output size, quantization tables, CRC, and total core byte size.

## Important APIs, Types, and Functions
Notable offsets include `JASPER_INTERRUPT_MASK_OFFSET`, `JASPER_INTERRUPT_STATUS_OFFSET`, `JASPER_RESET_OFFSET`, `JASPER_CORE_CTRL_OFFSET`, `JASPER_STATUS_OFFSET`, `JASPER_INPUT_CTRL0/1_OFFSET`, `JASPER_IMAGE_SIZE_OFFSET`, input/output base registers, output size/max size registers, luma/chroma quantization table offsets, CRC registers, and `JASPER_CORE_BYTE_SIZE`.

## Control Flow
No code flow. Hardware helper functions use these constants for read-modify-write and busy-polled register programming.

## State and Persistence
Represents volatile MMIO register layout only. The hardware stores programmed state while powered.

## Dependencies and Integration Points
Included by `e5010-jpeg-enc-hw.h` and used by `e5010-jpeg-enc-hw.c`. It pairs with `e5010-mmu-regs.h` for MMU control.

## Risks
Mask/shift mismatches can corrupt unrelated register fields. Address registers use alignment masks that must match DMA address requirements. Quantization table offsets must match the 64-entry table packing used by the driver.

## Test Signals
Hardware encode smoke tests, interrupt enable/status/clear tests, max-size overflow IRQ tests, QP table quality changes, and register trace comparison against vendor documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-core-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc-hw.c

## Purpose
Hardware access layer for the E5010 JPEG encoder. It wraps MMIO register field writes, busy polling, reset, MMU bypass, interrupt control/status/clear, clock/CRC/input setup, DMA base addresses, image dimensions, strides, quantization tables, output size, and encode start.

## Important APIs, Types, and Functions
`write_reg_field()` performs masked writes; `write_reg_field_not_busy()` waits for `JASPER_BUSY` to clear before programming most fields. Exported helper functions include `e5010_reset()`, `e5010_hw_bypass_mmu()`, interrupt enable/status/clear helpers, clock gating and CRC toggles, input source/address/subsampling/chroma-order setters, stride and image size setters, `e5010_hw_set_output_max_size()`, `e5010_hw_set_qpvalue()`, `e5010_hw_get_output_size()`, and `e5010_hw_encode_start()`.

## Control Flow
The main driver initializes the device by bypassing the MMU, configuring clocking/CRC/input source, and enabling IRQs. For each job it programs addresses, dimensions, strides, subsampling, chroma order, max output size, then starts encoding. On busy-programming errors it resets the core/MMU.

## State and Persistence
State is hardware MMIO state. No software state is kept except stack temporaries.

## Dependencies and Integration Points
Depends on Linux `io.h`, `iopoll.h`, device logging, `e5010-core-regs.h`, and `e5010-mmu-regs.h`. Called exclusively by the V4L2 E5010 driver.

## Risks
Busy polling uses atomic polling with a 50 ms timeout; long hardware operations may fail configuration. `e5010_hw_enable_manual_clock_gating()` ignores its `enable` argument and always writes 0, likely intentional for disabling but surprising. Address setters pass shift 0 with masks that encode alignment bits, so callers must already provide appropriately aligned DMA addresses.

## Test Signals
Register programming traces, reset timeout injection, output address error IRQ, picture done IRQ, quality-control QP table updates, MMU bypass verification, and encode start/complete tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc-hw.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc-hw.h

## Purpose
Declares the E5010 hardware helper API used by the V4L2 driver and includes the core/MMU register maps.

## Important APIs, Types, and Functions
Prototypes cover IRQ enable/status/clear, clock gating, CRC, input source and geometry, luma/chroma/output DMA addresses, output size, strides, subsampling, chroma order, quantization table writes, reset, output max size, encode start, and MMU bypass.

## Control Flow
No implementation flow. It defines the call surface used by probe/init, mem2mem job programming, IRQ handling, and error reset.

## State and Persistence
No software state. Functions operate on caller-provided `void __iomem *` bases and hardware state.

## Dependencies and Integration Points
Includes `e5010-core-regs.h` and `e5010-mmu-regs.h`. Used by `e5010-jpeg-enc.c` and implemented by `e5010-jpeg-enc-hw.c`.

## Risks
Prototype/base naming uses `core_offset` but actual values are MMIO bases; misuse with wrong base region would program invalid registers. Header lacks include guards for Linux types itself and relies on includers or included register headers for `u32`, `bool`, and `struct device`.

## Test Signals
Compile coverage for both implementation and main driver, plus runtime tests for every declared helper via encode, IRQ, reset, and quality-control paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc-hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc.c

## Purpose
Implements a V4L2 mem2mem baseline JPEG encoder driver for Imagination E5010 hardware. It exposes YUV420/YUV422 semiplanar input formats, JPEG capture output, compression quality control, crop selection, vb2 queueing, JPEG header generation, IRQ completion, platform probe/remove, and runtime/system PM.

## Important APIs, Types, and Functions
Format table `e5010_formats[]` defines NV12/NV12M/NV21/NV21M/NV16/NV16M/NV61/NV61M output and JPEG capture. Ioctl handlers include querycap, enum/try/get/set format, enum framesizes, get/set selection, event subscription, and encoder command. Queue operations include `queue_init()`, `e5010_queue_setup()`, `e5010_buf_prepare()`, `e5010_buf_queue()`, `e5010_buf_finish()`, start/stop streaming, and `e5010_device_run()`. Control handling is via `V4L2_CID_JPEG_COMPRESSION_QUALITY`, `calculate_qp_tables()`, and `update_qp_tables()`. Platform entry points are `e5010_probe()` and `e5010_remove()`.

## Control Flow
Probe allocates/registers V4L2 and video devices, initializes mem2mem, maps `core` and `mmu` resources, requests IRQ, gets clock, enables runtime PM, and registers `/dev/video0`-style node. Open allocates `struct e5010_context`, creates mem2mem queues, initializes controls and default formats. Stream-on powers the device and calls `e5010_init_device()`. `e5010_device_run()` locks hardware, selects next src/dst buffers, copies metadata, updates QP tables when context or quality changed, computes crop offsets, programs DMA addresses and image parameters, sets output max size, and starts encoding. IRQ removes buffers, handles output-address error or picture done, marks EOS on last draining source buffer, sets capture payload to hardware output size plus header size, and finishes the mem2mem job. `e5010_buf_finish()` writes the JPEG header into the capture buffer after successful completion.

## State and Persistence
Device state in `struct e5010_dev` includes V4L2/mem2mem/video devices, MMIO bases, clock, mutex, hardware spinlock, and `last_context_run` for QP table caching. Per-file `struct e5010_context` holds output/capture queue data, crop, quality, QP tables, update flag, and control handler. No disk state exists.

## Dependencies and Integration Points
Uses V4L2 core, V4L2 mem2mem, vb2 DMA-contig, JPEG helper tables, media JPEG constants, runtime PM, platform OF matching (`img,e5010-jpeg-enc`), E5010 hardware helpers, and DMA API with a 32-bit mask.

## Risks
Capture header is written in `buf_finish()` after IRQ payload calculation, so capture buffers must be CPU-mapped and large enough for `HEADER_SIZE`. Crop adjustment logic contains suspicious corrections when crop exceeds bounds, and should be tested for right/bottom edge cases. The driver registers with fixed requested video nr 0, which can collide and fall back only if core permits. Runtime PM puts occur per queue stop and gets per queue start, so asymmetric stream-on/off order needs coverage. Error IRQ path can process both error and picture-done flags if both are set.

## Test Signals
`v4l2-compliance`, JPEG encode with each supported input format, quality control changes across contexts, crop tests for alignment and bounds, drain/EOS commands, output buffer too small error IRQ, streamoff during active job, suspend/resume with queued contexts, and JPEG header validation by decoding produced files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc.h

## Purpose
Private header for the E5010 JPEG encoder driver. It defines JPEG/header constants, format limits, queue/device/context/buffer structures, chroma order and subsampling enums, and the format descriptor type.

## Important APIs, Types, and Functions
Constants include `MAX_PLANES`, `HEADER_SIZE`, min/max/default dimensions, module name, JPEG markers, Huffman/quantization marker lengths, component/sampling constants, and QP table sizing. Important structures are `struct e5010_q_data`, `struct e5010_dev`, `struct e5010_context`, `struct e5010_buffer`, and `struct e5010_fmt`. Inline `to_e5010_context()` converts a file handle to per-context state.

## Control Flow
No runtime flow beyond the inline container conversion. The constants guide JPEG header writing, QP generation, format negotiation, queue sizing, and hardware programming in the C file.

## State and Persistence
Defines in-memory state. `e5010_q_data` persists queue format, dimensions, sizeimage, bytesperline, sequence, crop, and crop flag. `e5010_context` persists quality and QP tables per open file. `e5010_dev` persists platform-device lifetime hardware and V4L2 state.

## Dependencies and Integration Points
Includes V4L2 controls/device/file-handle headers and is included by both the main driver and hardware-facing code indirectly through shared types.

## Risks
`HEADER_SIZE` must cover the generated marker/header bytes exactly enough for all supported formats. Fixed `MAX_PLANES` of 2 matches semiplanar formats but would need changes for planar formats. The unused `struct e5010_ctrl` appears legacy and may invite drift.

## Test Signals
Compile coverage, format negotiation for all listed formats, JPEG header size validation, QP table generation at quality 1/75/100, and crop/sequence state tests per context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-jpeg-enc.h -->
