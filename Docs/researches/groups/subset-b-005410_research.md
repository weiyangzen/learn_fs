# subset-b-005410 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_defs.h

Purpose: `sh_css_defs.h` is a shared macro contract for the AtomISP CSS host and firmware-side pipeline generator. It defines bit depths, gain/fraction shifts, sensor and continuous-mode geometry limits, Bayer downscaling factor encodings, shading/morph/statistics table dimensions, viewfinder sizing rules, and ISP internal width/height calculations. The file is intentionally macro-heavy because many values must be usable in preprocessor expressions and must match ISP/SP firmware assumptions.

Important APIs/types/functions: this header exports constants rather than C functions. Key groups are `SH_CSS_*_SHIFT` fixed-point precision values, `SH_CSS_BDS_FACTOR_*` plus `PACK_BDS_FACTOR()`, ISP pipe version macros, RGB gamma and CCM bit-depth definitions, sensor and continuous sensor limits, morph table layout macros, shading table sizing macros such as `_ISP_SCTBL_WIDTH_PER_COLOR()`, ISP2401 shading variants, 3A grid sizing macros, VF output sizing macros, and internal frame geometry macros like `__ISP_INTERNAL_WIDTH()` and `_ISP_MAX_INPUT_WIDTH()`.

Control flow and state: there is no runtime control flow or persistence. The effective behavior is compile-time branching on hardware constants such as `ISP_VMEM_DEPTH` and expression composition in later binary selection/configuration code. Runtime users feed frame dimensions, decimation factors, crop flags, and mode bits into these macros to derive aligned buffers and firmware-visible sizes.

Dependencies and integration: it includes `<linux/math.h>` for helpers like `DIV_ROUND_UP()` and `isp.h` for `ISP_VEC_NELEMS`, `HIVE_ISP_DDR_WORD_BYTES`, and VMEM/DDR geometry. It is used by parameter packing, shading, MIPI, binary description, and internal ABI code. The comments explicitly note that it cannot include some VAMEM headers because it is visible to ISP/pipeline generator code.

Risks: many macros have implicit assumptions about vector width, word size, even crop positions, and firmware ABI compatibility. Because they are macros, callers can pass expressions with side effects or values that underflow, especially in crop/padding calculations. Changes to constants can silently alter buffer sizes and break HMM allocations, SP DMEM layouts, or firmware expectations.

Test signals: valuable tests are compile-time build coverage across ISP2400/ISP2401 constants, static assertions in consumers, binary selection tests that validate BDS masks, and runtime stream setup tests for maximum/minimum resolutions, shading table sizes, 3A grid dimensions, DVS envelope handling, and internal width alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_firmware.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_firmware.c

Purpose: `sh_css_firmware.c` loads and decomposes the AtomISP CSS firmware blob supplied to the driver. It validates the top-level firmware header, records the release version, builds the global SP firmware descriptor, builds ISP blob descriptors for all ISP binaries, copies metadata offsets needed for parameter programming, and releases all allocated firmware-side host metadata on unload.

Important APIs/types/functions: global outputs are `sh_css_sp_fw`, `sh_css_blob_info`, and `sh_css_num_binaries`; callers access `sh_css_get_fw_version()`, `sh_css_check_firmware_version()`, `sh_css_load_firmware()`, `sh_css_unload_firmware()`, `sh_css_load_blob()`, and `sh_css_load_blob_info()`. Internal `setup_binary()` vmallocs and copies SP blob code, patches `blob.data`, and remembers allocation ownership in `fw_minibuffer`. `struct firmware_header` overlays the file header and first binary header; `struct fw_param` tracks duplicated names and buffers for cleanup.

Control flow: `sh_css_load_firmware()` rejects null or too-small firmware, checks `h_size`, copies the version string, calls `sh_css_check_firmware_version()`, allocates ISP descriptor storage and `fw_minibuffer`, then iterates each `ia_css_fw_info`. For each entry it calls `sh_css_load_blob_info()`, bounds-checks `blob.offset + blob.size`, logs type-specific details, enforces SP at `SP_FIRMWARE`, and stores ISP descriptors after `NUM_OF_SPS`. `sh_css_load_blob_info()` validates blob size decomposition and PMEM alignment, duplicates SP/ISP names, and copies ISP parameter/config/state memory offset structures into a compact allocated block.

State and persistence: firmware state is held in file-static `firmware_header`, `fw_minibuffer`, `FW_rel_ver_name`, and exported global descriptors. `sh_css_unload_firmware()` frees duplicated names and copied buffers, clears `sh_css_sp_fw`, frees `sh_css_blob_info`, and resets the binary count. `sh_css_load_blob()` allocates HMM memory and stores raw blob bytes for CSS DMA access.

Dependencies and integration: this file depends on HMM allocation/storage, kernel `kmalloc`/`vmalloc`, `ia_css_fw_info` blob ABI, ISP memory-offset structures, `IS_ISP2401`, and firmware type enumerations. Later binary selection and parameter code consumes `sh_css_blob_info`, while MMU/SP code consumes `sh_css_sp_fw`.

Risks: several early error exits in `sh_css_load_firmware()` occur after allocations without local unwind, so callers must be careful to call unload on failure paths or leaks can remain. Version mismatch currently logs but returns false, so incompatible firmware is accepted. `sh_css_load_blob_info()` trusts firmware-provided offset fields after partial validation; malformed offsets can produce invalid reads if the top-level size relationship is not enough. `setup_binary()` stores allocated code through `fw_minibuffer`, making the cleanup table critical.

Test signals: tests should load valid and malformed firmware blobs, including wrong `h_size`, bad `binary_nr`, SP not at index 0, non-ISP later binaries, bad blob size sums, bad PMEM alignment, out-of-range offsets, allocation failures, and unload-after-partial-load. Runtime signals include version logging, non-null SP firmware code/data, expected ISP descriptor count, and clean refcount/memory leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_firmware.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_firmware.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_firmware.h

Purpose: `sh_css_firmware.h` is the public host-side interface for loaded CSS firmware state. It defines the firmware file header format visible to user-supplied firmware blobs and declares the global descriptors and loader helpers implemented in `sh_css_firmware.c`.

Important APIs/types/functions: `struct sh_css_fw_bi_file_h` contains a 64-byte version string, binary count, and header size. Extern globals are `sh_css_sp_fw`, `sh_css_blob_info`, and `sh_css_num_binaries`. The exported functions are `sh_css_get_fw_version()`, `sh_css_check_firmware_version()`, `sh_css_load_firmware()`, `sh_css_unload_firmware()`, `sh_css_load_blob()`, and `sh_css_load_blob_info()`.

Control flow and state: the header itself has no executable logic. It defines the contract that callers use before initializing the SP, selecting ISP binaries, and copying blobs into HMM memory. The global variables represent persistent loaded-firmware state and are reset by the implementation during unload.

Dependencies and integration: it includes `system_local.h`, `ia_css_err.h`, and `ia_css_acc_types.h` for `ia_css_ptr`, firmware descriptors, acceleration types, and error conventions. It forward-declares `struct device` so loader calls can log through Linux device APIs without forcing all users to include device headers. It is included by internal CSS code, MMU code, and parameter/binary selection paths.

Risks: this header exposes mutable global firmware state, so ordering matters: consumers must not use `sh_css_sp_fw` or `sh_css_blob_info` before successful load or after unload. The header does not encode ownership rules; `sh_css_blob_info` points to allocated implementation-owned memory and must not be freed by consumers.

Test signals: compile tests should ensure all consumers see consistent prototypes. Integration tests should exercise firmware load/unload ordering and verify users fail gracefully when globals are unset or binary counts are invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_firmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_frac.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_frac.h

Purpose: `sh_css_frac.h` provides small fixed-point fitting helpers for converting 16-bit host-side signed and unsigned coefficients into the ISP vector element precision. It centralizes the shifts and clamp ranges used by parameter encoders such as MACC table conversion.

Important APIs/types/functions: macros derive signed and unsigned register bit counts from `ISP_VEC_ELEMBITS`, define host-to-ISP shift values, fraction fitting macros, and signed/unsigned ISP min/max ranges. `sDIGIT_FITTING(int v, int a, int b)` right-shifts a signed value from 16-bit precision into ISP precision and clamps it. `uDIGIT_FITTING(unsigned int v, int a, int b)` does the same for unsigned coefficients.

Control flow and state: both helpers are pure inline functions with no persistent state. They compute `fit_shift`, apply the base shift, optionally apply additional fractional-bit reduction, and clamp the result with `clamp_t()`.

Dependencies and integration: it includes `<linux/minmax.h>` and `mamoiada_params.h`, which supplies `ISP_VEC_ELEMBITS`. `sh_css_params.c` uses `sDIGIT_FITTING()` when converting MACC coefficients for ISP pipe version 1. The same formulas must remain aligned with firmware expectations for vector element width.

Risks: the macros assume sensible `a` and `b` values; a negative or unexpectedly large shift count would be undefined in C. Precision loss is deliberate but easy to misapply if callers pass fraction bit counts for a different source format. The signed minimum uses `1 << uISP_REG_BIT`, so integer width and shift validity depend on `ISP_VEC_ELEMBITS`.

Test signals: unit coverage should feed boundary values, negative signed values, maximum unsigned values, and combinations where `fit_shift` is positive, zero, and negative. Parameter tests should compare packed MACC values against known firmware reference tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_frac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_host_data.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_host_data.c

Purpose: `sh_css_host_data.c` is a tiny allocation wrapper for host-side byte buffers that are later copied into HMM/DDR parameter memory. It gives callers a uniform `struct ia_css_host_data` containing a 32-bit size and an address allocated with kernel virtual memory helpers.

Important APIs/types/functions: `ia_css_host_data_allocate(size_t size)` allocates the wrapper with `kmalloc_obj()`, stores `size` as `uint32_t`, and allocates `address` with `kvmalloc()`. `ia_css_host_data_free(struct ia_css_host_data *me)` releases `address` with `kvfree()`, nulls the pointer, and frees the wrapper.

Control flow and state: there is no global state. Allocation is two-stage and unwinds the wrapper if the payload allocation fails. Free is null-safe.

Dependencies and integration: it includes `ia_css_host_data.h` for the data structure and `sh_css_internal.h` for local allocation helpers/macros. `sh_css_params.c` uses this abstraction when converting FPN, shading, and morph tables into ISP memory layout before storing through `hmm_store()`.

Risks: `size_t` is truncated to `uint32_t` in `me->size`, which is acceptable only if all CSS host data buffers fit in 32 bits. Callers assume `address` is initialized and `size` matches the payload length; mismatches can produce partial or excessive HMM stores. The helper does not zero the payload.

Test signals: allocation failure injection should cover wrapper and payload failure. Parameter conversion tests should verify allocated `size` equals the bytes passed to `hmm_store()`, and large-size tests should guard against truncation if future callers can request buffers above 4 GiB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_host_data.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_hrt.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_hrt.c

Purpose: `sh_css_hrt.c` provides low-level host runtime checks around SP/ISP hardware state. In this subset it implements idleness detection and a simple wait loop for SP completion or software interrupt notification.

Important APIs/types/functions: `sh_css_hrt_system_is_idle()` reads SP and ISP idle bits and checks every FIFO monitor channel for valid queued data. `sh_css_hrt_sp_wait()` polls until the SP idle bit is set or a SW interrupt bit appears in the IRQ controller status register. The header declares additional SP start functions, but this file only implements idle and wait.

Control flow and state: `sh_css_hrt_system_is_idle()` accumulates `not_idle`, emits warnings for a non-idle SP, non-idle ISP, or non-empty FIFO channel, and returns the inverse. `sh_css_hrt_sp_wait()` busy-waits with `udelay(1)` while both "not idle" and "no SW interrupt" remain true, then returns 0. Neither function persists state.

Dependencies and integration: it uses inline accessors from `event_fifo.h`, `sp.h`, `isp.h`, `irq.h`, and `fifo_monitor.h`, plus `IA_CSS_WARNING` logging. It is used around CSS pipeline lifecycle and by parameter/shading code indirectly through runtime checks.

Risks: `sh_css_hrt_sp_wait()` has no timeout, so a wedged SP without an interrupt can spin indefinitely. Idleness relies on hardware register correctness and may race with concurrent SP/ISP activity. FIFO warnings are diagnostic only and do not identify owners of pending data.

Test signals: hardware or emulator tests should cover idle and busy SP/ISP states, pending FIFO data, SW interrupt wakeup, and stuck-SP timeout behavior at higher layers. Static review should confirm callers do not invoke the unbounded wait from contexts that cannot tolerate polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_hrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_hrt.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_hrt.h

Purpose: `sh_css_hrt.h` declares host runtime entry points for controlling and observing SP/ISP execution in the CSS driver. It is a small boundary between higher-level CSS code and lower-level SP/ISP hardware accessors.

Important APIs/types/functions: declarations include `sh_css_hrt_sp_start_si()`, `sh_css_hrt_sp_start_copy_frame()`, `sh_css_hrt_sp_start_isp()`, `sh_css_hrt_sp_wait()`, and `sh_css_hrt_system_is_idle()`. The start functions are implemented elsewhere in the driver, while wait and idle are implemented in `sh_css_hrt.c`.

Control flow and state: the header has no state. Its APIs imply lifecycle flow: configure SP/ISP work, start a specific SP path, optionally wait, then check system idleness.

Dependencies and integration: it includes `sp.h`, `isp.h`, and `ia_css_err.h`. Consumers include stream/pipeline control and diagnostic code that needs SP and ISP identifiers or error conventions.

Risks: exposing multiple start functions without state typing means callers must know which start path matches the current SP program and firmware state. `sh_css_hrt_sp_wait()` is declared as returning an int but currently always returns 0, so callers cannot rely on timeout/error reporting.

Test signals: compile/link tests should ensure all declared start functions have implementations. Integration tests should verify correct sequencing for start, wait, and idle checks across copy frame, sensor input, and ISP execution paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_hrt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_internal.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_internal.h

Purpose: `sh_css_internal.h` is the core private ABI contract for the AtomISP CSS host, SP, and ISP interface. It defines command/event enums, pipeline and stage structures, host-to-SP communication blocks, HMM buffer payloads, circular queue layouts, SP configuration, and prototypes for parameter/pipeline helper functions. Many structures are copied directly to SP/ISP memory, so layout stability is central to the file.

Important APIs/types/functions: key enums are `sh_css_order_binaries`, `host2sp_commands`, `sh_css_sp_event_type`, `sh_css_stage_type`, port direction/type enums, and `sh_css_queue_type`. Important structures include `sh_css_ddr_address_map`, `ia_css_isp_parameter_set_info`, `sh_css_binary_args`, `sh_css_sp_config`, `sh_css_sp_pipeline`, `ia_css_frames_sp`, `sh_css_isp_stage`, `sh_css_sp_stage`, `sh_css_sp_group`, `sh_css_sp_output`, `sh_css_hmm_buffer`, `host_sp_communication`, and `host_sp_queues`. The header also exports helpers such as `sh_css_params_init()`, `sh_css_params_uninit()`, `sh_css_update_uds_and_crop_info()`, `sh_css_store_sp_group_to_ddr()`, and pipe lookup/accessors.

Control flow and state: this is declarative, but it defines state machines used elsewhere: host commands use a depth-one ready/command handshake, SP events are converted into public event masks, pipelines carry running/stage/thread/port/QOS state, host-SP queues carry buffer and event descriptors, and metadata flags track processed/offline/wait-input state. `static_assert()` checks tie C host layouts to firmware-expected sizes.

Dependencies and integration: it includes Linux build/math/stdarg support, CSS public types, firmware descriptors, legacy pipe IDs, frame/statistics/metadata types, DMA constants, circular buffer ABI, buffer queue interfaces, timer types, input system/formatter headers, and `sh_css_defs.h`. It is included broadly by firmware loading, MIPI, HRT, parameter, stream, and SP bridge code.

Risks: this header is high blast radius. Field order and size changes can break firmware ABI even when C compiles. Some comments explicitly prohibit enums/bools in firmware-visible structures because host and hivecc representations can differ. Queue depths and constants must match SP firmware assumptions. The `SIZE_OF_*` macros must be updated with any struct changes or the static asserts will fail; if asserts are bypassed, runtime corruption is likely.

Test signals: the strongest tests are compile-time `static_assert()` coverage on every supported architecture/compiler, SP/host queue integration tests, event conversion tests that keep enum order synchronized with public event IDs and SP code, pipeline serialization tests for `sh_css_store_sp_group_to_ddr()` and stage storage, and runtime tests for metadata/MIPI/frame buffer queue exchange.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_legacy.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_legacy.h

Purpose: `sh_css_legacy.h` preserves legacy CSS pipe identifiers and API entry points used by older AtomISP host code. It distinguishes legacy pipe roles and carries extra pipe configuration knobs that are not represented directly in the newer public pipe config.

Important APIs/types/functions: `enum ia_css_pipe_id` defines preview, copy, video, capture, YUVPP, and count values. `struct ia_css_pipe_extra_config` carries booleans for raw binning, YUV downscaling, high speed, DVS 6-axis, reduced pipe, fractional downscaling, and disabling VF post-processing. Declared functions include `ia_css_pipe_create_extra()`, `ia_css_pipe_extra_config_defaults()`, `ia_css_temp_pipe_to_pipe_id()`, deprecated `sh_css_set_black_frame()`, and ISP2400 `sh_css_enable_cont_capt()`.

Control flow and state: this header is declarative. The pipe ID enum is used as an array index and must match `IA_CSS_PIPE_ID_NUM` expectations in internal pipeline state. Extra config is passed at pipe creation to influence binary selection and pipeline construction.

Dependencies and integration: it includes CSS public frame, pipe, stream, type, and error headers. `sh_css_internal.h` depends on this enum for `NR_OF_PIPELINES`, pipeline arrays, and queue/event mask sizes. `sh_css_params.c` implements `sh_css_set_black_frame()` and uses pipe IDs for per-pipe DVS and parameter maps.

Risks: enum order is ABI-like inside this driver because arrays are indexed by pipe ID and firmware-visible structures use related constants. Legacy functions can still mutate modern stream state, especially black-frame/FPN configuration. Extra config booleans are loosely typed and can encode invalid combinations that later binary selection rejects.

Test signals: tests should cover default extra config values, mapping temporary pipes to legacy IDs, pipe creation for each mode, and deprecated black-frame behavior when FPN is enabled or disabled. Compile-time checks should keep `NR_OF_PIPELINES` aligned with `IA_CSS_PIPE_ID_NUM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_legacy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_metrics.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_metrics.c

Purpose: `sh_css_metrics.c` implements lightweight frame and program-counter metrics for CSS binaries. It can count processed frames and, when enabled, build ISP/SP PC histograms of run versus stall samples for the active binary.

Important APIs/types/functions: exported global `sh_css_metrics` holds the binary metrics list and frame counters. `sh_css_metrics_start_frame()` increments frame count. `sh_css_metrics_enable_pc_histogram()` toggles sampling. `sh_css_metrics_start_binary()` selects the current binary histograms, allocates arrays sized by `ISP_PMEM_DEPTH` and `SP_PMEM_DEPTH`, and links the binary metrics into the global list. `sh_css_metrics_sample_pcs()` reads ISP PC and sink registers and updates histogram buckets. Helpers `clear_histogram()`, `make_histogram()`, and `insert_binary_metrics()` manage arrays and list insertion.

Control flow and state: the file maintains static `pc_histogram_enabled`, `isp_histogram`, and `sp_histogram`. Sampling is a no-op unless enabled. Starting a binary sets the active histogram pointers and lazily allocates bucket arrays. ISP sampling updates `msink[pc]` by bitwise-and, classifies stalls when sink is not `0x7FF`, and increments `stall` or `run`. SP sampling code is compiled but disabled by `&& 0`.

Dependencies and integration: it uses SP/ISP control register accessors and internal CSS metrics structures from `sh_css_metrics.h`. Higher-level code can call start-frame/start-binary/sample around pipeline execution to collect diagnostics.

Risks: `make_histogram()` can partially allocate `run` or `stall` then fail on a later array, leaving non-null partial state with `length == 0`; later calls return early if `run` is set, so allocation failure handling is weak. `insert_binary_metrics()` asserts `*l`, yet callers pass `&sh_css_metrics.binary_metrics`, which can be NULL initially; depending on assert behavior this may be wrong. PC values read from hardware are used as array indices without bounds checks. Histogram arrays are never freed in this file.

Test signals: diagnostic tests should enable/disable histograms, start first and repeated binaries, simulate allocation failures, and sample boundary PC values. Static/dynamic analysis should check list insertion with an initially empty list and out-of-range PC reads. Runtime debug output should show frame counts and nonzero run/stall buckets when sampling is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_metrics.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_metrics.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_metrics.h

Purpose: `sh_css_metrics.h` defines CSS runtime metrics structures and declares the metrics control/sampling functions. It is the public-private contract used by pipeline code to track frame counts and optional PC histograms.

Important APIs/types/functions: `struct sh_css_pc_histogram` stores length plus `run`, `stall`, and `msink` arrays. `struct sh_css_binary_metrics` stores binary mode/id, ISP and SP histograms, and next pointer. `struct ia_css_frame_metrics` holds `num_frames`. `struct sh_css_metrics` combines a linked list of binary metrics and frame metrics. Declared functions are `sh_css_metrics_enable_pc_histogram()`, `sh_css_metrics_start_frame()`, `sh_css_metrics_start_binary()`, and `sh_css_metrics_sample_pcs()`.

Control flow and state: this header has no logic. The extern `sh_css_metrics` represents persistent process/driver metrics state managed by `sh_css_metrics.c`.

Dependencies and integration: it includes `type_support.h` and then `ia_css_types.h` after the structure definitions because `ia_css_binary.h` depends on metrics definitions. Users include it when embedding `sh_css_binary_metrics` in binary descriptors or invoking sampling hooks.

Risks: the histogram arrays are raw pointers with no ownership annotations in the type definition, so lifetime management is implicit. Linked-list ownership of `sh_css_binary_metrics` also depends on caller-provided storage remaining valid while metrics are collected.

Test signals: compile tests should confirm include ordering does not create circular dependencies. Runtime tests should verify metrics remain valid across binary lifetimes and are reset or freed by the owning code path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_metrics.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mipi.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mipi.c

Purpose: `sh_css_mipi.c` computes MIPI frame buffer sizes, allocates/free per-port buffered-sensor MIPI frames and metadata, and sends allocated buffer handles to the SP. It bridges stream input configuration, global CSS buffer state, and SP host-to-device communication.

Important APIs/types/functions: `ia_css_mipi_frame_calculate_size()` calculates a complete CSI/MIPI frame size in DDR memory words including SOF/EOF, packet headers, optional SOL/EOL, embedded data, RAW/YUV/RGB packing, and ISP2401 padding. `mipi_init()` clears per-port allocation refcounts. `allocate_mipi_frames()` allocates `my_css.mipi_frames` and optional metadata for buffered-sensor streams. `free_mipi_frames()` decrements per-port refs and frees buffers when refs reach zero, or frees all buffers when called with NULL. `send_mipi_frames()` writes frame/metadata pointers and frame counts to host-to-SP state and posts `IA_CSS_PSYS_SW_EVENT_MIPI_BUFFERS_READY`.

Control flow and state: file-static `ref_count_mipi_allocation[N_CSI_PORTS]` tracks shared port allocations, especially for ISP2401 multi-stream same-port use. Allocation bypasses online ISP2401 and non-buffered-sensor modes. It validates the CSI port, optionally computes 2401 buffer size, increments refs, sets `NUM_MIPI_FRAMES_PER_STREAM`, allocates frames, and allocates metadata if configured. Freeing validates mode/port, decrements refs, and releases frames/metadata at zero. Sending requires buffered sensor mode, valid port, SP running, and enqueues the SP event.

Dependencies and integration: it depends on stream/pipe/frame/metadata APIs, `my_css` global state from internal CSS, format-to-bits helpers, `HIVE_ISP_DDR_WORD_BYTES`, `ISP_VEC_NELEMS`, SP update functions, and buffer queue event APIs. It is invoked during stream setup and SP startup for buffered sensor input.

Risks: allocation failure after metadata allocation can leave earlier frames or metadata unless all paths unwind consistently; metadata allocation failure returns the previous `err` value, which may still be zero. Refcounting is per port, so mismatched allocate/free calls can leak or prematurely free shared buffers. Size calculations duplicate older logic and include comments questioning which stream config field is authoritative. Arithmetic uses unsigned dimensions and could overflow on invalid resolutions.

Test signals: tests should cover every input format size calculation, ISP2400 versus ISP2401 padding, YUV420 odd/even line math, embedded data, SOL/EOL, invalid formats, invalid ports, multi-stream same-port refcounts, allocation failure unwind, metadata allocation, NULL free-all behavior, and SP-not-running send failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mipi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mipi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mipi.h

Purpose: `sh_css_mipi.h` declares the local CSS MIPI buffer lifecycle helpers used by stream and pipeline setup code. It keeps MIPI initialization, allocation, free, and SP handoff behind a small interface.

Important APIs/types/functions: declarations are `mipi_init()`, `allocate_mipi_frames(struct ia_css_pipe *pipe, struct ia_css_stream_info *info)`, `free_mipi_frames(struct ia_css_pipe *pipe)`, and `send_mipi_frames(struct ia_css_pipe *pipe)`.

Control flow and state: the state is implemented in `sh_css_mipi.c` via per-port refcounts and global `my_css` frame/metadata arrays. Callers are expected to initialize once, allocate during stream setup, send before or during SP execution, and free during stream teardown.

Dependencies and integration: it includes CSS error/types/stream public headers for `ia_css_pipe`, `ia_css_stream_info`, and stream configuration types. It pairs with public `ia_css_mipi.h`, which provides frame size calculation declarations.

Risks: the header does not document ownership or valid modes, so misuse is easy: only buffered-sensor modes need buffers, online ISP2401 bypasses allocation, and NULL free has special "free all" semantics.

Test signals: lifecycle tests should call the declared functions in normal and teardown paths and validate no buffers remain in global state after free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mipi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mmu.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mmu.c

Purpose: `sh_css_mmu.c` connects the CSS driver to the hardware MMU and SP TLB invalidation path. It invalidates SP-side DMA proxy translation state when the SP is running and updates all MMU devices with a new page table base index.

Important APIs/types/functions: `ia_css_mmu_invalidate_cache()` checks `sh_css_sp_is_running()`, obtains the SP firmware `invalidate_tlb` address from `sh_css_sp_fw`, and stores `true` to the SP DMEM symbol `ia_css_dmaproxy_sp_invalidate_tlb`. `sh_css_mmu_set_page_table_base_index(hrt_data base_index)` loops over `N_MMU_ID`, calls `mmu_set_page_table_base_index()`, and invalidates each MMU cache.

Control flow and state: the cache invalidation path is conditional on SP running so DMEM is not touched before SP initialization. The page-table update path is synchronous and iterates all MMU IDs without storing additional state in this file.

Dependencies and integration: it depends on `ia_css_mmu` APIs, SP running state from `sh_css_sp.h`, loaded SP firmware offsets from `sh_css_firmware.h`, SP DMEM accessors, and `mmu_device.h`. It is part of memory mapping setup and invalidation after HMM/page table changes.

Risks: if firmware offset metadata is wrong or the SP firmware is not loaded, the invalidate flag can target the wrong DMEM address. `sh_css_mmu_set_page_table_base_index()` assumes all MMU IDs accept the same base index and always invalidates immediately; failures are not reported. The local `HIVE_ADDR_...` variable is assigned but not directly used except to silence warnings, so the actual symbol address comes from `sp_address_of()`.

Test signals: integration tests should update page table bases and verify DMA translations change only after invalidation. SP-running and SP-not-running cases should be covered. Firmware load tests should verify `sh_css_sp_fw.info.sp.invalidate_tlb` is populated before invalidation paths are used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_dvs.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_dvs.c

Purpose: `sh_css_param_dvs.c` allocates, initializes, copies, and frees DVS 6-axis coordinate tables and translates ISP DVS statistics into host structures. These tables drive digital video stabilization coordinate warping for luma and chroma planes.

Important APIs/types/functions: internal `alloc_dvs_6axis_table()` allocates the config wrapper and four coordinate arrays. `init_dvs_6axis_table_from_default()` fills unity/default coordinates from frame resolution and DVS offset. `init_dvs_6axis_table_from_config()` copies an existing table. Exports are `generate_dvs_6axis_table()`, `generate_dvs_6axis_table_from_config()`, `free_dvs_6axis_table()`, `copy_dvs_6axis_table()`, and `ia_css_dvs_statistics_get()`.

Control flow and state: allocation chooses dimensions from either a source config or frame resolution using macros from `sh_css_param_dvs.h`; it then allocates Y x/y and UV x/y arrays and unwinds on failure. Default initialization walks each grid and stores coordinates shifted by `DVS_COORD_FRAC_BITS`, with UV offsets half of Y offsets and chroma block height. Copy helpers assert matching dimensions and memcpy the four arrays. Statistics dispatch selects DVS1 or DVS2 conversion based on `enum dvs_statistics_type`.

Dependencies and integration: it depends on DVS table geometry macros, CSS debug/assert/type headers, and statistics conversion helpers such as `ia_css_get_dvs_statistics()` and `ia_css_get_dvs2_statistics()`. `sh_css_params.c` uses these tables when generating per-pipe DVS 6-axis parameter buffers and user-visible DVS2 6-axis configs.

Risks: assertions enforce dimension invariants but may be compiled out, after which mismatched tables can overflow during `memcpy()`. Coordinate size arithmetic uses unsigned products and should be validated for overflow on large resolutions. Comments contain legacy YUV420 assumptions; other formats may not match UV sizing. `ia_css_dvs_statistics_get()` silently does nothing for unknown types.

Test signals: tests should allocate and free tables for small, odd, and maximum resolutions, verify default coordinate formulas, copy between same-sized tables, inject allocation failures at each array, and translate both DVS and DVS2 statistics. Sanitizer tests should check dimension mismatch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_dvs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_dvs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_dvs.h

Purpose: `sh_css_param_dvs.h` defines the DVS table geometry and declares the DVS 6-axis table helpers. It is the shared sizing contract used by the DVS table allocator and the main ISP parameter writer.

Important APIs/types/functions: macros define minimum DVS envelope, block dimensions for luma/chroma, block count rounding, table dimensions, coordinate fraction bits, input bytes per pixel, xmem alignment, `DVS_6AXIS_COORDS_ELEMS`, `DVS_6AXIS_BYTES(binary)`, and the supported GDC interpolation mode. Declarations cover `generate_dvs_6axis_table()`, `generate_dvs_6axis_table_from_config()`, `free_dvs_6axis_table()`, and `copy_dvs_6axis_table()`.

Control flow and state: no runtime state exists. The macros determine allocation sizes and DDR buffer sizes at runtime when invoked with frame or binary dimensions. `DVS_NUM_BLOCKS_X()` rounds luma horizontal blocks to an even count, while chroma uses direct rounded-up block count.

Dependencies and integration: it includes Linux math helpers, `math_support.h`, CSS public types, and `gdc_global.h` for `gdc_warp_param_mem_t`. `sh_css_params.c` uses `DVS_6AXIS_BYTES(binary)` to size DVS parameter buffers and `sh_css_param_dvs.c` uses table dimension macros to allocate coordinate arrays.

Risks: `DVS_6AXIS_BYTES(binary)` currently references only `out_frame_info[0]` and assumes two outputs have the same resolution, as the comment states. Format assumptions are YUV420-like for UV dimensions. Size macros can overflow if binary resolution is invalid or unbounded.

Test signals: geometry tests should verify luma/chroma block and table sizes for even/odd widths, minimum envelope handling, and DDR byte counts for binaries with DVS enabled. Integration tests should compare generated buffer sizes against firmware consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_dvs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_shading.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_shading.c

Purpose: `sh_css_param_shading.c` allocates, frees, generates, crops, and interpolates lens shading correction tables. It prepares sensor-space shading data for the grid dimensions and padding requirements of a selected ISP binary.

Important APIs/types/functions: internal `crop_and_interpolate()` performs bilinear interpolation from an input shading table to an output table while accounting for cropped target dimensions and left/right/top padding. `sh_css_params_shading_id_table_generate()` creates an identity shading table filled with 1s and zero fraction bits. `prepare_shading_table()` chooses identity output when input is absent or crops/interpolates an input table for a binary, BDS factor, sensor binning, and ISP padding. `ia_css_shading_table_alloc()` and `ia_css_shading_table_free()` manage table objects and per-color planes.

Control flow and state: interpolation computes source grid positions for each output color plane, clamps source indices at sensor/table edges, and calculates a weighted bilinear result. `prepare_shading_table()` derives input resolution from the binary, adjusts left/right/top padding for BDS and sensor binning, clips to input sensor dimensions, allocates the target table, and processes every `IA_CSS_SC_NUM_COLORS` plane. There is no global state.

Dependencies and integration: it depends on shading public types, binary descriptors, BDS fraction helper `sh_css_bds_factor_get_fract()`, `sh_css_defs.h` sizing rules, and allocation/logging helpers. `sh_css_params.c` calls it in legacy shading conversion mode and stores the resulting table to DDR.

Risks: the interpolation math is sensitive to zero or one table dimensions because it divides by `width - 1` and `height - 1`. Padding arithmetic mixes signed and unsigned values; negative right padding is accepted as an `int` and later contributes to padded width. Legacy conversion mode can allocate temporary tables repeatedly. Identity table generation does not set sensor dimensions, which is fine for ISP identity use but may surprise callers inspecting metadata.

Test signals: tests should cover identity generation, null input fallback, all four color planes, padding cases described in the comment, BDS factors, sensor binning shifts, small table dimensions, edge clamping, and allocation failure cleanup. Golden-image or table-golden tests are especially useful for interpolation correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_shading.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_shading.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_shading.h

Purpose: `sh_css_param_shading.h` declares the shading table generation/preparation helpers used by the CSS parameter writer. It separates shading-specific table work from the much larger parameter manager.

Important APIs/types/functions: `sh_css_params_shading_id_table_generate()` allocates an identity shading table of a requested width and height. `prepare_shading_table()` prepares an input shading table for a specific binary, sensor binning, and BDS factor and returns a target table.

Control flow and state: the header contains no state. The implementation allocates returned tables, and callers are responsible for freeing them with `ia_css_shading_table_free()` unless ownership is retained in stream parameter state.

Dependencies and integration: it includes `ia_css_types.h` and `ia_css_binary.h` for shading table and binary descriptors. `sh_css_params.c` calls these helpers when `IA_CSS_SC_ID` parameters need to be written to DDR.

Risks: ownership is not obvious from the prototypes: both functions write through `struct ia_css_shading_table **target_table`, and callers must handle NULL on allocation failure and cleanup existing temporary tables before overwriting pointers.

Test signals: compile tests should ensure the header remains lightweight. Integration tests should exercise parameter updates with no shading table, direct table use, and legacy conversion mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_param_shading.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params.c

Purpose: `sh_css_params.c` is the main AtomISP CSS host parameter manager. It owns default ISP configuration state, stream and per-frame ISP parameter objects, conversion of high-level CSS configs into firmware parameter memory, HMM/DDR buffer allocation and refcounting, SP parameter queue submission, shading/FPN/MACC/morph/DVS special handling, statistics allocation/translation helpers, metadata allocation, GDC LUT storage, and SP/ISP stage/group serialization.

Important APIs/types/functions: initialization and teardown include `sh_css_params_init()`, `sh_css_params_uninit()`, `ia_css_stream_isp_parameters_init()`, and `ia_css_stream_isp_parameters_uninit()`. Configuration entry points include `ia_css_stream_set_isp_config()`, `ia_css_stream_set_isp_config_on_pipe()`, `ia_css_pipe_set_isp_config()`, `ia_css_pipe_get_isp_config()`, and `sh_css_param_update_isp_params()`. Buffer/table helpers include `ia_css_params_store_ia_css_host_data()`, `ia_css_params_alloc_convert_sctbl()`, `ia_css_params_store_sctbl()`, morph table alloc/free/default generation, metadata alloc/free, 3A/DVS/DVS2 statistics and coefficient alloc/free, DVS2 6-axis config alloc/free, `sh_css_set_black_frame()`, GDC LUT functions, `sh_css_store_sp_group_to_ddr()`, `sh_css_store_sp_stage_to_ddr()`, `sh_css_store_isp_stage_to_ddr()`, `sh_css_invalidate_params()`, and UDS/crop helpers.

Control flow: global init allocates per-pipe/per-stage SP and ISP stage HMM blocks, configures default gamma/CTC/RGB/XNR tables, and allocates global DDR address map and SP group blocks. Stream init creates `ia_css_isp_parameters`, initializes defaults, allocates base DDR buffers for UDS and MACC, and creates per-pipe referenced maps. Setting config either updates global stream params or creates a per-frame params object, copies global state, applies the supplied config, and calls `sh_css_param_update_isp_params()` when commit is allowed. The update path processes zoom/motion per pipeline, applies changed kernel parameters per stage, writes special buffers to DDR, copies/refcounts the DDR address map into `ia_css_isp_parameter_set_info`, enqueues it to the SP parameter queue, posts a buffer-enqueued event, and dequeues old parameter buffers.

State and persistence: persistent state includes static global HMM pointers `sp_ddr_ptrs`, `xmem_sp_group_ptrs`, `xmem_sp_stage_ptrs`, `xmem_isp_stage_ptrs`, `default_gdc_lut`, the temporary interleaved LUT buffer, global enqueue/dequeue counters, and per-stream `isp_params_configs` plus `per_frame_isp_params_configs`. Parameter objects track changed flags, per-pipe DDR maps and sizes, DVS table pointers, FPN/shading/morph table state, UDS per stage, and parameter IDs/output-frame targeting. Refcount pools `IA_CSS_REFCOUNT_PARAM_SET_POOL` and `IA_CSS_REFCOUNT_PARAM_BUFFER` own HMM allocations that may be referenced by queued SP parameter sets.

Dependencies and integration: this file integrates nearly every CSS subsystem: HMM, GDC, ISP memory parameter APIs, buffer queues, SP events, stream/pipe/pipeline descriptors, binary descriptors, shading and DVS helpers, refcount pools, all host kernel parameter encoders, frame/metadata/statistics structures, and hardware memory layout constants from `sh_css_defs.h` and `sh_css_internal.h`.

Risks: this is a high-risk shared module. Buffer lifetime relies on reference counting and correct dequeue of SP parameter sets; queue stalls can retain HMM allocations. Many allocation paths are multi-stage and require careful unwind. `sh_css_create_isp_params()` can return `-ENOMEM` after assigning `*isp_params_out`, leaving partially allocated maps for caller cleanup. The update path clears changed flags after a multi-pipeline loop, so partial errors must be handled carefully. Some paths intentionally continue after DPC+BDS validation errors for internal testing. Morph/DVS/shading size arithmetic can overflow or mismatch firmware expectations if binary dimensions are invalid. `sh_css_store_sp_group_to_ddr()` uses a fixed 8192-byte staging buffer and manually serializes different ISP2401 layouts, making ABI drift dangerous.

Test signals: required coverage includes init/uninit leak tests, stream init/uninit for every pipe mode, global versus per-frame config updates, SP-not-running commit behavior, queue enqueue/dequeue/refcount balance, allocation failure injection in every special buffer path, FPN black-frame conversion, shading identity/direct/legacy conversion, MACC conversion for ISP pipe versions 1 and 2.2, DVS 6-axis default generation and storage, morph default table storage, metadata/statistics allocation/free, GDC LUT replacement after stream start, UDS/crop calculations with DVS envelope, zoom region validation, and SP group/stage DDR serialization size/layout checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params.c -->
