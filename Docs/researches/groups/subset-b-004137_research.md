# subset-b-004137 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda_regs.h

## Purpose
`coda_regs.h` is the register ABI map for the Chips&Media CODA VPU driver. It has no executable logic; its purpose is to give the CODA driver stable symbolic names for memory-mapped register offsets, command mailbox registers, command ids, codec mode ids, bit masks, and field packing helpers across CODADX6, CODA7, and CODA9 hardware generations.

## Important APIs, Types, and Constants
The header exports preprocessor definitions only. Key groups are the basic BIT processor control registers (`CODA_REG_BIT_CODE_RUN`, `CODA_REG_BIT_BUSY`, `CODA_REG_BIT_RUN_COMMAND`, interrupt and reset registers), static firmware buffer registers (`CODA_REG_BIT_CODE_BUF_ADDR`, `CODA_REG_BIT_WORK_BUF_ADDR`, stream/frame memory control), command values (`CODA_COMMAND_SEQ_INIT`, `CODA_COMMAND_PIC_RUN`, `CODA_COMMAND_SET_FRAME_BUF`, `CODA_COMMAND_FIRMWARE_GET`), codec mode constants for decode and encode, and per-command mailbox offsets for decoder sequence init, decoder picture run, encoder sequence init, encoder parameter change, encoder picture run, frame buffer setup, header generation, firmware version reads, CODA9 GDI, and CODA9 JPEG.

## Control Flow and Integration
Control flow is indirect: other CODA source files write these offsets through MMIO accessors before issuing commands via `CODA_REG_BIT_RUN_COMMAND` and polling or interrupting on busy/status registers. The same mailbox address range has different meanings depending on the active command, so call sites must choose the macro family matching the command they are about to issue.

## State and Persistence
The file defines volatile hardware state, not kernel-persistent state. Register writes program firmware buffers, stream pointers, decoded/encoded frame state, SRAM use, JPEG state, and command arguments in the VPU. Values persist in hardware until reset, overwritten by a later command, or cleared by firmware.

## Dependencies and Risks
The header depends on Linux bit helpers such as `BIT()` being available through including translation units. Risks are primarily ABI drift and macro misuse: many offsets overlap by design, generation-specific fields differ, and incorrect endian, stride, address, or mode constants can silently corrupt DMA or firmware state.

## Test Signals
Useful signals are successful CODA probe and firmware version query, clean decode/encode/JPEG smoke tests on hardware for each supported generation, absence of timeout on `CODA_REG_BIT_BUSY`, correct interrupt reasons, and media compliance tests that exercise sequence init, picture run, frame buffer registration, and JPEG paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/imx-vdoa.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/imx-vdoa.c

## Purpose
`imx-vdoa.c` implements the i.MX6 Video Data Order Adapter helper used by CODA workflows that need hardware-assisted video data reordering, especially tiled or VPU-oriented source layout into linear V4L2 capture formats. It is a platform driver plus exported helper API for clients that create a VDOA context, configure dimensions and output format, submit one DMA transfer, and wait for completion.

## Important APIs, Types, and Functions
The exported API is `vdoa_context_create`, `vdoa_context_configure`, `vdoa_device_run`, `vdoa_wait_for_completion`, and `vdoa_context_destroy`. Internal state is split between `struct vdoa_data` for device-wide MMIO, clock, and current context, `struct vdoa_ctx` for per-client completion and job counters, and `struct vdoa_q_data` for source/destination geometry. `vdoa_probe` binds the DT node, sets a 32-bit DMA mask, maps registers, acquires the clock, and installs the threaded IRQ.

## Control Flow
Clients allocate and configure a context, then call `vdoa_device_run(ctx, dst, src)`. The function serializes with an existing `curr_ctx` by waiting for it, stores the new context, reinitializes completion, programs control, frame size, input/output base addresses, strides, chroma offsets, and enables transfer/error interrupts before writing `VDOASRR_START`. The IRQ disables interrupts, acknowledges `VDOAIST`, logs transfer errors or spurious interrupts, increments `completed_job`, and completes the waiter.

## State and Persistence
Device state is transient and MMIO-backed. `curr_ctx` serializes one in-flight transfer; `submitted_job` and `completed_job` guard completion waits. Context creation enables the VDOA clock and destruction waits for an active transfer before disabling the clock and freeing memory.

## Dependencies and Integration
The driver depends on platform resources, DT compatible `fsl,imx6q-vdoa`, `clk`, `dma-mapping`, completions, IRQ threading, and V4L2 pixel format constants. It integrates with CODA through `imx-vdoa.h` exports and with the kernel device model through `module_platform_driver`.

## Risks and Test Signals
Risks include weak global serialization with no explicit lock around `curr_ctx`, fixed 300 ms timeout, 32-bit DMA address truncation into `u32`, strict width/height multiple-of-16 validation, and limited format validation despite an NV21 branch in run setup. Test with concurrent context users, timeout/error IRQ injection, NV12 and YUYV transfers, invalid dimensions, stream teardown during transfer, and runtime module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/imx-vdoa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/imx-vdoa.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/imx-vdoa.h

## Purpose
`imx-vdoa.h` is the public integration header for the optional i.MX VDOA helper. It lets CODA code compile both with and without `CONFIG_VIDEO_IMX_VDOA` by exposing real function prototypes when the driver is enabled and harmless inline stubs when it is not.

## Important APIs and Types
The header forward-declares `struct vdoa_data` and `struct vdoa_ctx`, keeping the implementation opaque. The API surface is `vdoa_context_create`, `vdoa_context_configure`, `vdoa_context_destroy`, `vdoa_device_run`, and `vdoa_wait_for_completion`. The enabled configuration expects `u32` pixel formats and `dma_addr_t` buffer addresses from the including context.

## Control Flow and Integration
CODA users can probe for VDOA availability by calling `vdoa_context_create`; when the config is disabled it returns `NULL`. Format validation can be performed through `vdoa_context_configure`, which returns success in the stub case so callers must separately handle a missing context if VDOA is required for a specific path.

## State and Persistence
The header itself owns no state. In the enabled path, state lives in the opaque context allocated by `imx-vdoa.c`. In the disabled path there is no persistent state, and all operations are no-ops.

## Dependencies and Risks
The conditional depends on `CONFIG_VIDEO_IMX_VDOA` or module form being visible to the preprocessor. The main risk is that stub `vdoa_context_configure` and `vdoa_wait_for_completion` return success, which is appropriate for optional acceleration but can mask accidental use of a missing context if call sites do not check the context pointer.

## Test Signals
Build coverage is the main signal: compile CODA with VDOA built-in, as a module, and disabled. Runtime tests should verify fallback behavior when `vdoa_context_create` returns `NULL` and successful reordering when the real platform device is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/imx-vdoa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/trace.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/trace.h

## Purpose
`trace.h` defines ftrace tracepoints for CODA VPU activity. It instruments firmware command submission/completion and buffer lifecycle points so developers can inspect decode, encode, JPEG, and bitstream FIFO behavior without adding ad hoc logging.

## Important APIs and Events
The file declares `TRACE_SYSTEM coda` and includes `linux/tracepoint.h`, `videobuf2-v4l2.h`, and `coda.h`. Direct events include `coda_bit_run` and `coda_bit_done`. Event classes reduce duplication for buffer events (`coda_buf_class`), buffer plus bitstream metadata events (`coda_buf_meta_class`), and metadata-only decoder events (`coda_meta_class`). Concrete events include `coda_enc_pic_run`, `coda_enc_pic_done`, `coda_bit_queue`, `coda_dec_pic_run`, `coda_dec_pic_done`, `coda_dec_rot_done`, `coda_jpeg_run`, and `coda_jpeg_done`.

## Control Flow and Integration
Call sites invoke generated `trace_coda_*` helpers around command and buffer transitions. The trace entries capture video-device minor, CODA context id, buffer index, command id, and ring-buffer metadata masked by `ctx->bitstream_fifo.kfifo.mask`. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` direct `trace/define_trace.h` to generate the event implementation from this header.

## State and Persistence
Tracepoints do not own device state. They sample live `struct coda_ctx`, `vb2_v4l2_buffer`, and `coda_buffer_meta` fields at the event point. Persistent output is external to the driver through ftrace/perf buffers when tracing is enabled.

## Dependencies and Risks
The header depends on stable `struct coda_ctx` fields (`fh.vdev`, `idx`, `bitstream_fifo`) and metadata layout. Risks include dereferencing context fields from poorly placed trace calls, misleading masked ring offsets if FIFO sizing changes, and build failures if the include path no longer matches the source tree.

## Test Signals
Build with tracing enabled, run decode/encode/JPEG workloads with `trace-cmd` or ftrace events enabled, and verify event ordering around bit commands, queued buffers, picture run/done, rotation done, and JPEG run/done. Tests should also compile with `TRACE_HEADER_MULTI_READ` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/Kconfig

## Purpose
`wave5/Kconfig` declares the `VIDEO_WAVE_VPU` kernel configuration option for the Chips&Media Wave5 stateful codec driver. It controls whether the Wave5 encoder/decoder driver is built and states the dependency envelope needed by the source files in this directory.

## Important Configuration
`VIDEO_WAVE_VPU` is a tristate named "Chips&Media Wave Codec Driver". It depends on V4L mem2mem driver support, `VIDEO_DEV`, device tree (`OF`), and either TI K3 architecture (`ARCH_K3`) or `COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, and `GENERIC_ALLOCATOR`.

## Control Flow and Integration
The option feeds the Wave5 Makefile via `obj-$(CONFIG_VIDEO_WAVE_VPU) += wave5.o`. Enabling it compiles the platform codec driver and causes module output named `wave5` when set to module. The selected dependencies match the driver's use of vb2 DMA-contiguous queues, vmalloc helpers, V4L2 mem2mem scheduling, and gen_pool SRAM allocation.

## State and Persistence
Kconfig has no runtime state. It persists as build configuration in `.config`, determines whether objects are present in the kernel or as a module, and gates runtime availability of Wave5 video devices.

## Dependencies and Risks
The architecture restriction limits normal builds to K3 unless compile-tested. Missing selected dependencies would break compilation or runtime queue setup. The help text says HEVC and H264 are supported; changes to actual format support should keep this text aligned.

## Test Signals
Signals are `allyesconfig`/`allmodconfig` compile coverage, `COMPILE_TEST` builds on non-K3 architectures, module build naming, and runtime probe on a DT platform with Wave5 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/Makefile

## Purpose
`wave5/Makefile` defines how the Wave5 driver is linked. It produces one composite object, `wave5.o`, when `CONFIG_VIDEO_WAVE_VPU` is enabled.

## Important Build Entries
The build target is `obj-$(CONFIG_VIDEO_WAVE_VPU) += wave5.o`. The composite object includes `wave5-hw.o`, `wave5-vpuapi.o`, `wave5-vdi.o`, `wave5-vpu-dec.o`, `wave5-vpu.o`, `wave5-vpu-enc.o`, and `wave5-helper.o`.

## Control Flow and Integration
There is no runtime control flow. Build integration ensures low-level hardware access, API wrappers, VDI memory/MMIO helpers, decoder frontend, platform device logic, encoder frontend, and shared helpers are linked into the same module or built-in object. This matters because many functions are cross-file internal driver APIs rather than separately exported module symbols.

## State and Persistence
The Makefile only controls build artifacts. Its persistent effect is the object composition used by the kernel build system.

## Dependencies and Risks
The Makefile depends on object names matching source files. Adding or removing Wave5 source files requires updating this list. A missing object can produce unresolved symbols, while stale entries break builds. The current list includes both decoder and encoder paths, matching the shared Kconfig description.

## Test Signals
Run kernel builds with `CONFIG_VIDEO_WAVE_VPU=y` and `m`, check that `wave5.o` or `wave5.ko` links without unresolved symbols, and verify incremental builds notice edits across all listed source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-helper.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-helper.c

## Purpose
`wave5-helper.c` provides shared utility code for Wave5 V4L2 encoder and decoder frontends. It centralizes state string conversion, instance cleanup, release sequencing, vb2 queue initialization, event subscription, output format reporting, format lookup, V4L2 format-to-firmware-standard mapping, queued buffer return, pixel format sizing, and IRQ FIFO allocation.

## Important APIs and Functions
Key functions include `state_to_str`, `wave5_kfifo_alloc`, `wave5_cleanup_instance`, `wave5_vpu_release_device`, `wave5_vpu_queue_init`, `wave5_vpu_subscribe_event`, `wave5_vpu_g_fmt_out`, `wave5_find_vpu_fmt`, `wave5_find_vpu_fmt_by_idx`, `wave5_to_vpu_std`, `wave5_return_bufs`, and `wave5_update_pix_fmt`. These operate on shared `struct vpu_instance` and `struct vpu_device` state from `wave5-vpu.h`.

## Control Flow
Open paths allocate instances and later call these helpers for queue setup and cleanup. Release first destroys the V4L2 mem2mem context, removes the instance from the device list under mutex plus spinlock protection, calls the codec-specific close function if firmware state exists, and then frees queues, controls, DMA buffers, SRAM, IDs, codec info, and the instance.

## State and Persistence
The helper owns no independent persistent storage, but it mutates important instance state: IRQ status kfifo allocation, queue parameters, V4L2 controls, source/destination format structures, SRAM and bitstream DMA buffers, framebuffer backing buffers, and device instance lists.

## Dependencies and Integration
It depends on V4L2 mem2mem, videobuf2 DMA-contig, V4L2 events/controls, IDA allocation, kfifo, and Wave5 VDI framebuffer reset/free helpers. It is shared by decoder and encoder frontends through `wave5-helper.h`.

## Risks and Test Signals
Risks include release ordering around IRQ threads, list synchronization between hard IRQ and threaded IRQ contexts, queue `buf_struct_size` consistency, and returning queued buffers with completed request controls. Test signals are clean open/close loops under active decode, event subscription behavior, buffer cancellation on streamoff/error paths, format enumeration/fallback behavior, and lockdep/KASAN coverage around release races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-helper.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-helper.h

## Purpose
`wave5-helper.h` declares the shared helper API used by Wave5 decoder and encoder source files. It keeps common V4L2, queue, format, and cleanup helpers in one interface.

## Important APIs and Types
The header includes `wave5-vpu.h`, defines `FMT_TYPES` as 2 and `MAX_FMTS` as 12, and declares helpers for instance state strings, cleanup/release, queue initialization, event subscription, output format get, format lookup by FourCC or index, V4L2-to-Wave standard mapping, returning queued buffers, updating multiplanar pixel formats, and IRQ kfifo allocation.

## Control Flow and Integration
Decoder and encoder open paths use `wave5_vpu_queue_init`, `wave5_kfifo_alloc`, and format helpers. Ioctl tables use `wave5_vpu_subscribe_event` and `wave5_vpu_g_fmt_out`. Release paths use `wave5_vpu_release_device` and `wave5_cleanup_instance`. The constants define fixed two-dimensional format arrays for codec and raw formats.

## State and Persistence
The header owns no state. It declares functions that operate on `struct vpu_instance`, `struct vpu_device`, vb2 queues, V4L2 file handles, and V4L2 pix formats owned elsewhere.

## Dependencies and Risks
The header depends on `wave5-vpu.h` for all core type definitions. `MAX_FMTS` is a coupling point: format arrays in frontend files must not exceed it, and lookup code treats zero FourCC entries as terminators.

## Test Signals
Compile decoder and encoder with this header, enumerate all format indices up to `MAX_FMTS`, exercise event subscriptions, and run open/release tests that prove the declarations match implementation signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-hw.c

## Purpose
`wave5-hw.c` is the hardware and firmware command backend for the Wave5 driver. It translates high-level decoder and encoder API requests into MMIO register programming, firmware commands, command/result queries, reset and sleep/wake sequences, framebuffer registration, bitstream pointer updates, and capability discovery.

## Important APIs and Functions
Core helpers include `wave5_vpu_is_init`, `wave5_vpu_get_product_id`, `wave5_vpu_init`, `wave5_vpu_re_init`, `wave5_vpu_sleep_wake`, `wave5_vpu_reset`, `wave5_vpu_get_version`, `wave5_vpu_clear_interrupt`, and internal command helpers such as `wave5_bit_issue_command`, `send_firmware_command`, and `wave5_send_query`. Decoder-facing APIs include `wave5_vpu_build_up_dec_param`, `wave5_vpu_dec_init_seq`, `wave5_vpu_dec_get_seq_info`, `wave5_vpu_dec_register_framebuffer`, `wave5_vpu_decode`, `wave5_vpu_dec_get_result`, display flag operations, bitstream flag operations, and read pointer get/set. Encoder-facing APIs include build-up, init sequence, sequence info, framebuffer registration, encode, encode result, finish sequence, and open-parameter validation.

## Control Flow
Initialization writes firmware into the common DMA buffer, clears command registers, programs remap pages, code/temp buffers, AXI parameters, product-specific task buffers, starts the VPU, checks firmware queue status, queries properties, and enables interrupts based on supported encoders/decoders. Runtime commands write mailbox registers, issue a command, poll busy status, then read success/fail registers. Decode flow creates an instance, initializes sequence, queries stream properties, registers compressed and linear framebuffers, sends picture commands, and queries output info. Encode flow similarly creates an instance, writes sequence/GOP/rate-control/crop/source parameters, registers reconstruction buffers, starts picture encode, and queries produced bitstream metadata.

## State and Persistence
Persistent driver state lives in `struct vpu_device` and `struct vpu_instance` codec info. This file updates common DMA memory, SRAM usage, work buffers, task buffers, stream read/write pointers, queue counts, sequence information, framebuffer auxiliary buffers, support flags, performance cycle counters, encoder open parameters, and firmware-visible display flags.

## Dependencies and Integration
It depends on `wave5-regdefine.h` for register offsets, `wave5-vdi` accessors for MMIO and DMA memory, `wave5-vpuapi` data structures, Linux polling helpers, bitfield helpers, and firmware command semantics. It is called by `wave5-vpuapi.c`, decoder/encoder V4L2 frontends, and platform probe/power management code.

## Risks and Test Signals
Risks include timeout handling, overlapping mailbox offsets, product-specific differences between WAVE515 and WAVE521 variants, DMA allocation cleanup on partial failures, secondary AXI size calculations marked TODO, queue count synchronization, 32-bit register writes of DMA addresses, and strict validation needed before firmware commands. Test signals include firmware boot/reinit/sleep/wake/reset on each product, decode/encode sequence init and frame runs, dynamic resolution changes, 8-bit and 10-bit capability checks, framebuffer allocation failure injection, queueing failure retry behavior, and media compliance with real H264/HEVC streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-regdefine.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-regdefine.h

## Purpose
`wave5-regdefine.h` is the register and firmware mailbox ABI definition for Wave5 hardware. It names command ids, query options, common registers, decoder mailboxes, encoder mailboxes, reset bits, remap controls, product registers, interrupt registers, GDI/backbone bus registers, and result fields.

## Important APIs and Constants
The file defines `enum W5_VPU_COMMAND` for firmware commands such as init, wake, sleep, create/destroy instance, init sequence, set framebuffer, picture run, query, and bitstream update. `enum query_opt` describes query modes including VPU info, results, display flag update, bitstream pointer operations, and debug info. Macro groups cover power/debug registers, FIO, interrupts, reset, remap, busy status, product identification, command/result status, bitstream options, common create-instance registers, set-framebuffer registers, decoder sequence/result registers, encoder sequence/set-param/picture/result registers, and bandwidth report registers.

## Control Flow and Integration
The header is consumed by `wave5-hw.c` and VDI code. Firmware command flow depends on writing command-specific arguments into shared offsets, issuing `W5_COMMAND`, then reading success, fail reason, queue status, and command-specific return registers. Many offsets intentionally overlap because the firmware interprets them based on the active command or query option.

## State and Persistence
The macros describe hardware-visible state. Registers persist across command phases until firmware, reset, or host code changes them. The definitions include state for firmware code remapping, VCPU program counter, interrupts, framebuffers, stream pointers, decoder display flags, encoder source buffers, rate control, and performance ticks.

## Dependencies and Risks
The header depends on Linux `BIT()` and register users including it in a context where bit helpers are available. Risks are ABI mismatch with firmware, wrong command context for an overlapping offset, missing product-specific differences, and comments for unsupported or unused registers becoming stale.

## Test Signals
Test by booting firmware, querying product info, running decoder and encoder init/picture/result commands, validating interrupt reason bits, exercising reset and sleep/wake, and comparing register programming against vendor documentation or known-good traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-regdefine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vdi.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vdi.c

## Purpose
`wave5-vdi.c` implements the Wave5 VDI layer: low-level register access, common firmware memory allocation, coherent DMA buffer allocation/free, safe memory writes/clears, array allocation helpers, and SRAM gen_pool allocation.

## Important APIs and Functions
Public functions include `wave5_vdi_init`, `wave5_vdi_release`, `wave5_vdi_write_register`, `wave5_vdi_read_register`, `wave5_vdi_clear_memory`, `wave5_vdi_write_memory`, `wave5_vdi_allocate_dma_memory`, `wave5_vdi_free_dma_memory`, `wave5_vdi_allocate_array`, `wave5_vdi_allocate_sram`, and `wave5_vdi_free_sram`. `wave5_vdi_allocate_common_memory` is the internal setup helper that chooses common buffer size by product code.

## Control Flow
`wave5_vdi_init` allocates common memory, validates product family, and clears a register range when the BIT processor is not running. MMIO helpers wrap `writel` and `readl`. DMA helpers allocate coherent buffers into `struct vpu_buf`, write bounded data into mapped buffers, clear buffers, and free them while zeroing metadata. SRAM helpers allocate from a gen_pool up to the smaller of configured SRAM size and available pool space.

## State and Persistence
State is stored in `struct vpu_device` buffers: `common_mem`, `sram_buf`, and arrays passed by higher layers. DMA memory persists until explicit free or device release. `wave5_vdi_release` nulls `vdb_register` and frees common memory.

## Dependencies and Integration
The file depends on `wave5-vpu.h`, `wave5-vdi.h`, `wave5-regdefine.h`, Linux DMA coherent APIs, MMIO accessors, and generic allocator APIs. It is the dependency beneath `wave5-hw.c` firmware and framebuffer paths.

## Risks and Test Signals
Risks include freeing zero-sized buffers returning `-EINVAL`, logging but still zeroing on free of an unmapped buffer, possible structure reuse in `wave5_vdi_allocate_array`, product-code size mismatch, and ensuring coherent allocations satisfy firmware address limits. Test signals are VDI init/release, DMA allocation failure injection, boundary checks in `wave5_vdi_write_memory`, SRAM pool exhaustion, repeated array resize/free cycles, and MMIO smoke reads of product registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vdi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vdi.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vdi.h

## Purpose
`wave5-vdi.h` declares the minimal low-level VDI interface and shared DMA buffer structure for Wave5 hardware access.

## Important APIs and Types
The header defines `VPU_PRODUCT_CODE_REGISTER`, register accessor macros `vpu_write_reg` and `vpu_read_reg`, and `struct vpu_buf` with `size`, DMA address `daddr`, and CPU virtual address `vaddr`. It declares `wave5_vdi_init` and `wave5_vdi_release`; additional VDI functions are implemented in `wave5-vdi.c` and used through other headers or visible declarations in included Wave5 headers.

## Control Flow and Integration
Higher layers use `vpu_write_reg` and `vpu_read_reg` to route register access to `wave5_vdi_write_register` and `wave5_vdi_read_register`. The `vpu_buf` structure is the common currency for firmware common memory, work buffers, bitstream ring buffers, framebuffer auxiliary buffers, and SRAM allocations.

## State and Persistence
The header owns no state. `struct vpu_buf` instances persist in `struct vpu_device`, codec info, and frame buffer arrays until freed by VDI helpers or cleanup paths.

## Dependencies and Risks
It depends on `wave5-vpuconfig.h` and Linux string, slab, and device headers. The header uses C++-style comments in a couple of places but remains accepted in kernel C. A risk is that only init/release are declared here while users may rely on declarations from other included headers for the rest of the VDI API; keeping prototypes centralized would reduce drift.

## Test Signals
Compile all Wave5 objects with sparse/W=1 style checks, verify accessor macro type correctness, and run init/release plus DMA buffer lifecycle tests through the higher-level driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vdi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu-dec.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu-dec.c

## Purpose
`wave5-vpu-dec.c` is the V4L2 mem2mem decoder frontend for Wave5 hardware. It exposes a stateful decoder video device, handles userspace ioctls and vb2 queues, feeds compressed bitstream into a firmware ring buffer, manages capture framebuffers, reacts to firmware completion, and reports EOS or dynamic resolution changes.

## Important APIs, Data, and Functions
The file defines decoder format tables for HEVC/H264 compressed OUTPUT and multiple raw CAPTURE formats. Important functions include state management (`switch_state`, `set_instance_state`), source consumption (`wave5_handle_src_buffer`), EOS handling (`wave5_vpu_dec_stop`, `send_eos_event`, `flag_last_buffer_done`), dynamic resolution handling (`handle_dynamic_resolution_change`), result completion (`wave5_vpu_dec_finish_decode`), ioctl handlers for format/selection/decoder commands, vb2 operations, ring-buffer fill/write helpers, mem2mem operations (`device_run`, `job_ready`, `job_abort`), open/release, and device register/unregister.

## Control Flow
Opening allocates a `vpu_instance`, V4L2 file handle, mem2mem context, controls, default formats, IRQ FIFO, instance id, optional SRAM, and links the instance into the device list. OUTPUT stream start allocates a bitstream ring buffer and opens a firmware decoder instance. The first mem2mem job fills the ring buffer, issues sequence init, waits for interrupt, reads initial info, and queues a source-change event. CAPTURE setup prepares compressed internal framebuffers and linear user buffers, then picture jobs submit decode commands. IRQ-thread completion calls `finish_process`, gets output info, advances consumed source buffers, returns displayed capture buffers, and handles EOS or resolution changes.

## State and Persistence
Instance state includes the VPU state machine (`NONE`, `OPEN`, `INIT_SEQ`, `PIC_RUN`, `STOP`), source/destination formats, colorimetry, bitstream DMA ring, read pointer tracking, remaining consumed bytes, queued counts, EOS/draining flags, framebuffer arrays, FBC allocation counts, display flags, and source-feed list protected by `feed_lock`. State persists across streaming transitions until release, with streamoff resetting buffer queues, display flags, ring pointers, and reallocation markers.

## Dependencies and Integration
The frontend depends on V4L2 mem2mem, vb2 DMA-contig buffers, runtime PM, Wave5 helper functions, `wave5-vpuapi` decoder API wrappers, Wave5 hardware backend, SRAM/VDI allocation, and platform registration in `wave5-vpu.c`. It integrates with userspace through ioctls, events (`V4L2_EVENT_EOS`, `V4L2_EVENT_SOURCE_CHANGE`), and standard stateful decoder semantics.

## Risks and Test Signals
Risks include complex state transitions under streamoff, EOS, queueing failure, dynamic resolution change, and IRQ completion; ring-buffer wrap accounting; minimum capture buffer enforcement; bitdepth/product restrictions; lock ordering between spinlocks, mutexes, and mem2mem callbacks; runtime PM balancing; and cleanup while firmware commands are pending. Test signals include v4l2-compliance stateful decoder tests, H264/HEVC decode with DRC, EOS and drain behavior, streamoff on each queue, capture buffer starvation, ring-buffer wrap with multiple source buffers, 10-bit rejection/support paths, queueing-failure retry, open/close races, and lockdep/KASAN runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/wave5-vpu-dec.c -->
