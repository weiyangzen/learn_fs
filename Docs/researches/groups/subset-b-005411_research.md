# subset-b-005411 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params.h

## Purpose
Defines the host-side ISP parameter aggregate for the AtomISP CSS pipeline and declares helpers for storing host parameter data and shared GDC lookup tables. It is the central header for stream, pipe, and stage parameter state consumed by SP/ISP staging code such as `sh_css_sp.c` and parameter-copy code.

## Important APIs, Types, and Functions
The main type is `struct ia_css_isp_parameters`, which stores UDS parameters per stage, stream optical-black config, FPN/motion/morphing/shading tables, gamma/CTC/MACC/XNR tables, many public `ia_css_*_config` blocks, DVS coefficients, change flags, per-pipe DDR pointer maps, and an `isp_parameters_id`. Declared APIs include `ia_css_params_store_ia_css_host_data()`, `ia_css_params_store_sctbl()`, `ia_css_params_alloc_convert_sctbl()`, `sh_css_pipe_isp_config_get()`, default GDC LUT map/free/get helpers, and `sh_css_pipe_get_pp_gdc_lut()`.

## Control Flow
The header has no runtime flow, but it defines the object that parameter setters populate and that pipeline initialization copies to CSS/DDR. `sh_css_sp.c` calls `sh_css_params_ddr_address_map()` and later copies binary memory interfaces to DDR, while GDC LUT access feeds SP pipeline setup.

## State and Persistence Behavior
Most fields persist across frames until their corresponding changed bit is consumed. Per-pipe/per-stage memory-change arrays drive selective parameter uploads. Pointer fields such as morph, shading, and DVS tables require strict lifetime ownership by the surrounding CSS code.

## Dependencies and Integration Points
Depends on AtomISP public type/config headers, binary/pipeline definitions, UDS/crop parameter types, and `sh_css_defs.h`. Integrates with ISP kernels generated from parameter metadata and with the SP stage serialization path.

## Risks
The struct is broad and ABI-like inside the driver: changing field names, array dimensions, or changed-bit semantics can silently desynchronize host parameter updates from firmware expectations. Pointer table ownership is easy to misuse because several fields are borrowed rather than embedded.

## Test Signals
Useful signals are successful pipeline start with changed ISP parameters, per-frame `isp_parameters_id` tracking, shading/morph/DVS table upload, default GDC LUT allocation/free, and no stale parameters after pipe/stage switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params_internal.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params_internal.h

## Purpose
Provides the minimal internal parameter-maintenance declaration for AtomISP CSS.

## Important APIs, Types, and Functions
Declares `sh_css_param_clear_param_sets()`, an internal routine used to clear or invalidate accumulated CSS parameter sets.

## Control Flow
No execution exists in this header. Callers include it when they need to reset parameter-set state outside the public `sh_css_params.h` contract.

## State and Persistence Behavior
The declared function implies global or shared parameter-set state owned elsewhere. Its safety depends on being called at pipeline teardown, reset, or configuration boundaries where stale parameter data must not leak into a later frame.

## Dependencies and Integration Points
No include dependencies beyond its guard. It is intentionally narrow to avoid exposing the full parameter struct internals to every user.

## Risks
Because the function has no parameters, it likely operates on hidden global state. Calling it while a pipeline is active could race with per-frame parameter upload or invalidate expected state.

## Test Signals
Reset/reconfigure tests should verify that old ISP parameter values are not reused after this routine is called and that active streaming paths are not disturbed by inappropriate clears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_params_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_properties.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_properties.c

## Purpose
Implements a small public query that reports static CSS/ISP properties to callers.

## Important APIs, Types, and Functions
`ia_css_get_properties(struct ia_css_properties *properties)` fills `gdc_coord_one`, `l1_base_is_index`, and `vamem_type`. It derives GDC unity from `gdc_get_unity(GDC0_ID) / HRT_GDC_COORD_SCALE`.

## Control Flow
The routine asserts a non-null output pointer, computes the truncated GDC coordinate scale, then stores fixed properties for L1 addressing and VAMEM type.

## State and Persistence Behavior
No persistent state is modified. The returned values are a snapshot of hardware/static platform properties and are stable for the lifetime of the driver instance.

## Dependencies and Integration Points
Depends on `ia_css_properties.h`, `ia_css_types.h`, `assert_support.h`, and `gdc_device.h`. The values are consumed by upper CSS users that need coordinate scaling or memory-model details.

## Risks
Assumes `GDC0_ID` is the relevant GDC instance and that truncating the full GDC coordinate scale is acceptable. Any platform with different VAMEM or L1 behavior would need this function updated.

## Test Signals
Callers should observe nonzero `gdc_coord_one`, `l1_base_is_index == true`, and `vamem_type == IA_CSS_VAMEM_TYPE_2` during CSS property queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_properties.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_sp.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_sp.c

## Purpose
Implements host-side construction, serialization, and control of AtomISP SP pipeline state. It translates `ia_css_pipeline` stages, frames, firmware binaries, metadata, queues, and event/command state into SP-visible DDR/DMEM structures and starts or controls the SP.

## Important APIs, Types, and Functions
Global stage state is held in `sh_css_sp_group`, `sh_css_sp_stage`, `sh_css_isp_stage`, private `sh_css_sp_output`, `per_frame_data`, and `sp_running`. Key entry points include `sh_css_sp_init_pipeline()`, `store_sp_stage_data()`, `store_sp_group_data()`, `sh_css_sp_start_binary_copy()`, `sh_css_sp_start_isp()`, `sh_css_write_host2sp_command()`, host2sp frame/metadata update functions, IRQ-mask functions, IF/input-circuit configuration, DMA debug-mask helpers, and `sh_css_sp_reset_global_vars()`. Important helpers include `sh_css_copy_frame_to_spframe()`, `set_input_frame_buffer()`, `set_output_frame_buffer()`, `sh_css_sp_init_stage()`, `sp_init_stage()`, and `configure_isp_from_args()`.

## Control Flow
Pipeline setup starts in `sh_css_sp_init_pipeline()`: it derives the SP thread id, clears the per-thread pipeline, counts stages, initializes group input configuration, records metadata and queue ids, then walks each stage. SP-only copy stages route to raw/isys copy setup; ISP/firmware stages route through `sp_init_stage()` and `sh_css_sp_init_stage()`, which copy binary/blob metadata, frame descriptors, queue-backed buffers, parameter DDR maps, crop offsets, ISP kernel configs, and state initialization. Each stage is stored to DDR, then the group address is stored in per-frame data. Runtime control writes host2sp commands and frame addresses into SP DMEM and starts the SP controller after cache invalidation.

## State and Persistence Behavior
The file relies on mutable global staging structs that are reused while building stages, with fields such as `program_input_circuit` explicitly preserved across clears and reset after storing. Per-frame state stores the current SP group address. Host2sp communication is persistent SP DMEM state for commands, offline frames, MIPI frames, metadata, raw-frame counts, and event masks. `sp_running` gates cache invalidation and SP start behavior.

## Dependencies and Integration Points
Depends on many AtomISP internals: HMM/MMU, binary metadata, queues, ISP parameter copy/configure functions, frame conversion, event public ABI, SP control, input formatter, GDC, DMA ids, and debug graph dumping. It is the bridge between high-level CSS pipeline objects and firmware symbols exposed by `sh_css_sp_fw`.

## Risks
Global staging structs are not inherently reentrant and are sensitive to pipe/thread ordering. Many address writes use firmware symbol offsets and `offsetof()` divided by `sizeof(int)`, so layout drift can break SP communication. Several paths assert on unsupported frame formats but still return errors that callers may not propagate. Firmware generation, ISP2400/ISP2401 differences, metadata queues, and continuous capture all introduce subtle branch-specific behavior.

## Test Signals
Good coverage includes raw copy, isys copy, binary copy, multi-stage ISP pipelines, metadata-enabled streams, continuous capture, memory-input streams, parameter sampling, SP start/stop, host2sp command readiness, MIPI/offline frame updates, IRQ masks, DMA debug masks, and reset/reinitialize cycles without stale frame descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_sp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_sp.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_sp.h

## Purpose
Declares the public host-side SP control and pipeline-staging interface for AtomISP CSS.

## Important APIs, Types, and Functions
Exports initialization/store calls (`sh_css_sp_store_init_dmem()`, `store_sp_stage_data()`, `store_sp_group_data()`), pipeline setup/teardown (`sh_css_sp_init_pipeline()`, `sh_css_sp_uninit_pipeline()`), copy start/status helpers, host2sp command and frame update routines, event IRQ mask initialization, SP running/start APIs, input formatter/circuit configuration, raw-pool and ISYS event toggles, DMA debug-mask functions, and global staging structs.

## Control Flow
Consumers include this header to build SP pipeline data before starting firmware, update dynamic frame slots while streaming, and control SP execution. The implementation in `sh_css_sp.c` performs the actual DDR/DMEM writes.

## State and Persistence Behavior
The exported globals expose shared mutable SP/ISP staging state. Callers must treat them as current pipeline-construction state rather than independent objects.

## Dependencies and Integration Points
Includes `system_global.h`, `type_support.h`, input formatter config, binary types, CSS public types, and pipeline definitions. It integrates with CSS pipeline creation, firmware boot, event handling, and debug paths.

## Risks
The broad API surface makes ordering important: stages must be initialized before stored, host2sp commands require firmware readiness, and dynamic frame updates must stay within fixed firmware arrays. Direct global access increases risk of stale or concurrent mutation.

## Test Signals
Compile coverage from pipeline, stream, and firmware-control units plus runtime checks for all declared update functions are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_sp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_stream_format.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_stream_format.c

## Purpose
Maps AtomISP input stream formats to bits per subpixel.

## Important APIs, Types, and Functions
`sh_css_stream_format_2_bits_per_subpixel(enum atomisp_input_format format)` returns bit depths for RGB, YUV, RAW, binary, and user-defined MIPI formats. Unknown formats return `0`.

## Control Flow
The function is a switch table from `atomisp_input_format` to 4, 5, 6, 7, 8, 10, 12, 14, or 16 bits per subpixel.

## State and Persistence Behavior
No state is read or written. Results are deterministic.

## Dependencies and Integration Points
Includes `sh_css_stream_format.h` and `ia_css_stream_format.h`. It feeds input-system, formatter, or MIPI sizing logic that needs bit-depth information.

## Risks
Returning `0` for new/unhandled formats can propagate into size calculations if callers do not validate it. User-defined formats are assumed 8-bit.

## Test Signals
Unit-level checks should cover every `ATOMISP_INPUT_FORMAT_*` enumerator used by sensors and verify unknown/default handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_stream_format.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_stream_format.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_stream_format.h

## Purpose
Declares the stream-format bit-depth helper for AtomISP CSS.

## Important APIs, Types, and Functions
Exports `sh_css_stream_format_2_bits_per_subpixel(enum atomisp_input_format format)`.

## Control Flow
No runtime flow in the header; callers include it before invoking the implementation in `sh_css_stream_format.c`.

## State and Persistence Behavior
No state.

## Dependencies and Integration Points
Depends on `ia_css_stream_format.h` for `enum atomisp_input_format`. Used by input system and stream configuration code.

## Risks
Any signature drift must match the C file and all callers.

## Test Signals
Compile coverage and bit-depth tests through the C implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_stream_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_struct.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_struct.h

## Purpose
Defines the global `struct sh_css` driver context for AtomISP CSS, separated from the historical `sh_css.h` naming.

## Important APIs, Types, and Functions
`struct sh_css` tracks active and all pipes, allocation/free/flush callbacks, ISP2401 extended allocation hooks, copy-preview stop flag, idle-check flag, continuous raw/MIPI frame arrays, metadata arrays, MIPI size checks, SP binary address, page-table base, deprecated memory sizing, IRQ type, pipe counter, and IPU type. Macros define `IPU_2400`, `IPU_2401`, `IS_2400()`, and `IS_2401()`, with `extern struct sh_css my_css`.

## Control Flow
The header defines context accessed across CSS setup, stream configuration, memory management, interrupt, and MIPI buffering paths. Runtime flow is in users of `my_css`.

## State and Persistence Behavior
`my_css` is long-lived global driver state. It persists pipe objects, current buffering state, platform type, and callback ownership across stream operations.

## Dependencies and Integration Points
Includes local system address maps and CSS public pipeline/pipe/frame/queue/IRQ headers. Integrates with code that allocates pipes, stores MIPI buffers, and branches between ISP2400 and ISP2401.

## Risks
The comment notes pipe-count assumptions tied to SP thread ids; expanding pipe object counts without revisiting arrays can break scheduling. Global mutable state and platform-type macros make concurrent or multi-device operation risky.

## Test Signals
Probe/init should set `my_css.type`, pipe create/destroy should update active/all arrays, continuous MIPI capture should fill frame and metadata arrays, and ISP2400/2401-specific paths should branch correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_struct.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_uds.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_uds.h

## Purpose
Defines compact UDS and crop-position structures shared between pipeline descriptions and CSS internals.

## Important APIs, Types, and Functions
Defines bit-size constants `SIZE_OF_SH_CSS_UDS_INFO_IN_BITS` and `SIZE_OF_SH_CSS_CROP_POS_IN_BITS`, plus `struct sh_css_uds_info` (`curr_dx`, `curr_dy`, `xc`, `yc`) and `struct sh_css_crop_pos` (`x`, `y`).

## Control Flow
No execution; these structs are embedded in pipeline or firmware-facing data.

## State and Persistence Behavior
Values represent per-stage/per-frame scaling and crop positions. They are plain data and persist wherever their parent pipeline structures persist.

## Dependencies and Integration Points
Depends on `type_support.h` for fixed-width `u16`. Used by `pipeline_global.h`, `sh_css_internal.h`, and UDS/crop configuration paths.

## Risks
The bit-size constants imply firmware/layout coupling. Widening fields or changing order can break SP/ISP interpretation.

## Test Signals
Scaling/crop tests should verify expected UDS deltas and crop positions are serialized into SP/ISP structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_uds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_version.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_version.c

## Purpose
Builds the reported AtomISP CSS plus firmware version string.

## Important APIs, Types, and Functions
`ia_css_get_version(char *version, int max_size)` selects `ISP2400_CSS_VERSION_STRING` or `ISP2401_CSS_VERSION_STRING` based on `IS_ISP2401`, appends `FW:` and `sh_css_get_fw_version()`, and returns `0` or `-EINVAL`.

## Control Flow
The function checks that the caller buffer can contain CSS version, firmware version, and separators, then uses `strscpy()` and `strcat()` to assemble the result.

## State and Persistence Behavior
No state is modified. It reads platform type and firmware-version state from other AtomISP components.

## Dependencies and Integration Points
Includes AtomISP Linux public headers, `ia_css_version.h`, generated `ia_css_version_data.h`, error definitions, and firmware version access.

## Risks
The size check must remain conservative because subsequent `strcat()` calls assume room. Version strings are compile-time/generated plus firmware-provided data.

## Test Signals
Queries on ISP2400 and ISP2401 should return the correct prefix, include firmware version text, terminate with `"; "`, and reject too-small buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_version.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/str2mem_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/str2mem_defs.h

## Purpose
Defines register ids, command bitfields, and alignment for the AtomISP stream-to-memory hardware block.

## Important APIs, Types, and Functions
Macros define command/status masks such as `_STR2MEM_CRUN_BIT`, `_STR2MEM_CMD_BITS`, `_STR2MEM_COUNT_BITS`, block/packet/byte command encodings, register ids for reset, endian, bit swapping, sync levels, read-post-write sync, dual-byte input, statistics update, and `_STR2MEM_REG_ALIGN`.

## Control Flow
No runtime flow. Hardware access code uses these constants to program or interpret stream-to-memory registers.

## State and Persistence Behavior
The constants encode persistent hardware register ABI.

## Dependencies and Integration Points
No includes. Integrated by low-level AtomISP input or test-stream paths that configure stream-to-memory movement.

## Risks
Typos or bit changes can corrupt command construction. The guard macro name uses `_ST2MEM_DEFS_H`, while the file is `str2mem_defs.h`, so include uniqueness relies on that exact historical spelling.

## Test Signals
Register programming tests should confirm generated commands have expected command/count bits and register ids align to hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/str2mem_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/streaming_to_mipi_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/streaming_to_mipi_defs.h

## Purpose
Defines bit positions for a streaming-to-MIPI word layout.

## Important APIs, Types, and Functions
Macros define valid bits for channels A/B, start/end of line, start/end of frame, channel-id LSB, and data-A LSB.

## Control Flow
No execution. Constants are used by code that packs or decodes synthetic MIPI stream words.

## State and Persistence Behavior
No mutable state; these constants model the persistent bit-level hardware/test protocol.

## Dependencies and Integration Points
No includes. Integrates with AtomISP input-system simulation, test pattern, or stream-to-MIPI conversion code.

## Risks
The definitions are bit-position contracts. Any shift change can mislabel frame boundaries or data bits.

## Test Signals
Bit-packing tests should verify SOL/EOL/SOF/EOF and channel id extraction for generated streaming-to-MIPI words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/streaming_to_mipi_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_global.h

## Purpose
Defines global AtomISP CSS hardware topology, memory classes, bus widths, device ids, and platform-wide constants shared by host and firmware-facing code.

## Important APIs, Types, and Functions
Important macros include DMA workaround flags, max burst lengths, HRT bus/register byte sizes, input formatter reset offsets/masks, memory counts, and `N_*` constants. It defines ids for DDR, ISP, SP, MMU, DMA, GDC, VAMEM, BAMEM, HMEM, IRQ, timers, GPIO, timed controller, input formatters, input system, RX, MIPI ports, subsystems, ISP memories, ISP2401 ISYS IRQ, IBUF controllers, stream2MMIO, CSI RX front/back ends and lanes, ISYS DMA, pixel generators, input ports, and DMA channels.

## Control Flow
No runtime flow. The enums size hardware base-address arrays and provide ids for low-level device APIs.

## State and Persistence Behavior
The file is static topology. Values are effectively ABI for register maps and firmware assumptions.

## Dependencies and Integration Points
Includes `hive_isp_css_defs.h`, `type_support.h`, and deprecated `hive_types.h`. Used throughout AtomISP PCI code, system-local maps, SP code, input formatter, MMU/DMA/GDC/timer drivers, and ISP2401 input system code.

## Risks
Changing ids or counts can misindex base-address arrays in `system_local.c` and can break preprocessor users that depend on `N_GDC_ID_CPP` or fixed port ids. The file mixes ISP2400 and ISP2401 topology, so platform-specific callers must still gate behavior correctly.

## Test Signals
Compile-time array sizing, probe-time register access on ISP2400/2401, input formatter reset, MMU/DMA/GDC operations, and MIPI port selection are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_local.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_local.c

## Purpose
Defines the concrete AtomISP MMIO/base-address map for all hardware blocks enumerated in `system_global.h`.

## Important APIs, Types, and Functions
Exports constant `hrt_address` arrays for ISP control/DMEM/BAMEM, SP control/DMEM, MMUs, DMA and ISYS2401 DMA, IRQ blocks, GDCs, FIFO monitor, GP device, GP timer, GPIO, timed controller, input formatters, input system, RX, IBUF controllers, ISYS IRQs, CSI RX FE/BE controllers, pixel generators, and stream2MMIO controllers.

## Control Flow
No logic; low-level accessors index these arrays by enum id to compute register addresses.

## State and Persistence Behavior
All data is read-only static address mapping.

## Dependencies and Integration Points
Includes `system_local.h`, which provides `hrt_address` and id counts. Integrates with hardware register drivers and SP/ISP control code.

## Risks
Address constants must match silicon. Enum count mismatches can cause build errors or out-of-bounds use in callers. The single `GP_TIMER_BASE` reflects interleaved timer registers, so consumers must not assume per-timer bases.

## Test Signals
Hardware bring-up should validate DEBI/MMIO access, SP/ISP DMEM/control reads, input formatter programming, and ISP2401 CSI/stream2MMIO register operations at these bases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_local.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_local.h

## Purpose
Declares the local AtomISP base-address map exported by `system_local.c`.

## Important APIs, Types, and Functions
Declares `GP_FIFO_BASE`, all `extern const hrt_address` base arrays for ISP/SP/MMU/DMA/IRQ/GDC/input-system blocks, and the single `GP_TIMER_BASE`.

## Control Flow
No execution. Callers include this header to access register base arrays.

## State and Persistence Behavior
The declared objects are immutable address-map state supplied by the C file.

## Dependencies and Integration Points
Defines `HRT_USE_VIR_ADDRS` under `HRT_ISP_CSS_CUSTOM_HOST`, includes `system_global.h` and deprecated `hive_types.h`. Used by hardware device accessors and CSS global structures.

## Risks
All declarations must stay synchronized with `system_local.c`. Virtual-address configuration affects host builds and address interpretation.

## Test Signals
Compile/link coverage for all extern arrays and runtime hardware access through each declared base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/system_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/timed_controller_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/timed_controller_defs.h

## Purpose
Defines register layout constants for the AtomISP timed controller block.

## Important APIs, Types, and Functions
Exports `_HRT_TIMED_CONTROLLER_CMD_REG_IDX` and `_HRT_TIMED_CONTROLLER_REG_ALIGN`.

## Control Flow
No execution. Timed-controller access code uses the command-register index and register alignment.

## State and Persistence Behavior
Constants encode stable hardware layout.

## Dependencies and Integration Points
No includes. Integrates with HRT/timed-controller low-level register helpers.

## Risks
Changing alignment or command index breaks register access.

## Test Signals
Timed-controller command programming should hit the expected register offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/timed_controller_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/version.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/version.h

## Purpose
Defines HRT interface version macros for AtomISP support code.

## Important APIs, Types, and Functions
Macros are `HRT_VERSION_MAJOR 1`, `HRT_VERSION_MINOR 4`, and `HRT_VERSION 1_4`.

## Control Flow
No execution.

## State and Persistence Behavior
Static version metadata only.

## Dependencies and Integration Points
No includes. Consumers can use it for compile-time compatibility checks or reporting.

## Risks
`HRT_VERSION 1_4` is token-style rather than a numeric expression, so consumers must use it consistently.

## Test Signals
Compile coverage where version macros are referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/Kconfig

## Purpose
Defines kernel configuration entries for the legacy AV7110 full-featured DVB card driver, optional IR/OSD support, and the SP8870 frontend dependency used by this driver family.

## Important APIs, Types, and Functions
Key symbols are `DVB_AV7110_IR`, `DVB_AV7110`, `DVB_AV7110_OSD`, and nested `DVB_SP8870`. `DVB_AV7110` depends on DVB core, PCI, I2C, and video device support, selects TTPCI EEPROM and SAA7146 video support, and auto-selects several DVB frontends/tuners when `MEDIA_SUBDRV_AUTOSELECT` is enabled.

## Control Flow
Kconfig selection determines whether `dvb-ttpci.o`, OSD code, IR code, and `sp8870.o` are built. Help text also documents required external firmware.

## State and Persistence Behavior
No runtime state. Configuration choices persist in the kernel build config and determine module availability.

## Dependencies and Integration Points
Integrates the av7110 directory with DVB core, media frontend drivers, RC core, SAA7146, and firmware-loading expectations.

## Risks
Missing selects/dependencies cause link errors or runtime probe failures. The driver requires external firmware, so enabling the module does not guarantee usable hardware without firmware files.

## Test Signals
Build matrix for built-in/module `DVB_AV7110`, OSD enabled/disabled, IR enabled when RC core is available, `MEDIA_SUBDRV_AUTOSELECT` on/off, and SP8870 firmware path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/Makefile -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/Makefile

## Purpose
Describes object composition and include paths for the AV7110 DVB driver build.

## Important APIs, Types, and Functions
`dvb-ttpci-objs` links `av7110_hw.o`, `av7110_v4l.o`, `av7110_av.o`, `av7110_ca.o`, `av7110.o`, `av7110_ipack.o`, and `dvb_filter.o`, with optional `av7110_ir.o`. `obj-$(CONFIG_DVB_AV7110)` builds `dvb-ttpci.o`, and `obj-$(CONFIG_DVB_SP8870)` builds `sp8870.o`.

## Control Flow
Kbuild uses the object list to form the module or built-in object based on Kconfig symbols.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
Adds include paths for DVB frontends, tuners, PCI TTP CI, and common media code, matching headers consumed by `av7110.c`.

## Risks
Object order and include paths matter for optional features and shared local headers. Removing `av7110_hw.o` or `av7110_av.o` breaks exported symbols used by the main driver.

## Test Signals
Successful compile/link for all Kconfig combinations, especially with `CONFIG_DVB_AV7110_IR` toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110.c

## Purpose
Main driver for SAA7146/AV7110 full-featured PCI DVB cards. It handles module parameters, PCI extension registration, firmware loading/validation, ARM watchdog recovery, IRQ tasklets, demux/feed control, frontend attachment, I2C helpers, full-TS/budget-patch capture, and device probe/remove.

## Important APIs, Types, and Functions
Important entry points include `av7110_attach()`, `av7110_detach()`, `av7110_irq()`, module init/exit, `ChangePIDs()`, `i2c_writereg()`, and `i2c_readreg()`. Internal core functions include `init_av7110_av()`, `recover_arm()`, `arm_thread()`, `debiirq()`, `gpioirq()`, `StartHWFilter()`, `StopHWFilter()`, feed start/stop/restart routines, `dvb_get_stc()`, firmware check/load helpers, many tuner `set_params` helpers, frontend wrappers, and `frontend_init()`.

## Control Flow
Probe allocates `struct av7110`, loads `dvb-ttpci-01.fw`, registers a DVB adapter and I2C adapter, configures full-TS or budget-patch DMA if requested/detected, initializes tasklets/locks/buffers/AV/CA, boots the AV7110 ARM firmware, starts an ARM monitor thread, registers demux/video/audio/CA/net devices, initializes analog/video and frontend support, and optionally IR. IRQs dispatch DEBI completion, GPIO mailbox, and VPE/full-TS capture to tasklets. Feeds either program firmware PID filters/recording paths or start software TS capture. Remove reverses the sequence and frees firmware, DMA, I2C, DVB, AV, CA, and tasklet resources.

## State and Persistence Behavior
Module parameters persist driver-wide: video mode, PID clearing, audio DAC, hardware sections, RGB, volume, budget/full-TS, WSS, TV standard, and debug. Per-card state lives in `struct av7110`: demuxes, pids, buffers, frontend saved SEC state, ARM loop counters, tasklets, and flags. Firmware images are vmalloc-backed until detach. Recovery reboots ARM firmware, restores AV setup and frontend SEC state, then restarts feeds.

## Dependencies and Integration Points
Integrates Linux PCI, firmware loader, I2C, DVB core/demux/net/frontend APIs, SAA7146 core/vv, many frontend modules, TTP CI EEPROM MAC parsing, AV/CA/HW helpers, V4L analog support, and optional IR/OSD.

## Risks
This file is concurrency-heavy: IRQ tasklets, DMA, kthread watchdog, demux callbacks, firmware commands, and userspace device operations share `struct av7110`. Error unwinding is long and must match allocation order. Firmware validation assumes exact blob layout and sizes. Full-TS/budget-patch register programming is hardware-specific and fragile. Frontend op wrapping must preserve original callbacks and saved SEC state.

## Test Signals
Probe/remove on supported PCI ids, missing/bad firmware errors, ARM boot/version query, watchdog recovery, frontend attach per subsystem id, PID filter start/stop, section and TS demux, memory playback, full-TS DMA capture, budget-patch detection, VPE tasklet packet delivery, I2C tuner programming, suspend-like teardown, and module parameter combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110.h

## Purpose
Central private header for the AV7110 driver. It defines debug helpers, playback/recording constants, video-event queues, IR/CI state, and the large per-device `struct av7110`.

## Important APIs, Types, and Functions
Key types include `struct av7110_p2t`, `struct dvb_video_events`, `struct infrared`, and `struct av7110`. The device struct owns DVB/V4L/SAA7146/I2C handles, analog tuner state, tasklets, audio DAC type, ring buffers, bitmap/OSD state, DEBI locks, playback/recording flags, CA slots/ring buffers, demuxes, full-TS DMA state, PID/frontend state, ARM firmware versions, firmware blob pointers, video/audio device pointers, ioctl mutex, crash-recovery callback, saved SEC commands, and wrapped frontend ops. It declares `ChangePIDs()`, IR hooks, I2C helpers, MSP helper, and analog/V4L init/exit.

## Control Flow
The header does not execute, but it is included by all AV7110 modules to share the per-card state layout and cross-file function contracts.

## State and Persistence Behavior
`struct av7110` is allocated at probe and persists until detach. Its fields are touched from IRQ tasklets, the ARM monitor thread, demux callbacks, userspace file operations, firmware command code, and remove/error paths.

## Dependencies and Integration Points
Includes Linux DVB audio/video/demux/CA/OSD/net APIs, media DVB core/demux/frontend/ringbuffer APIs, saa7146_vv, and supported frontend headers.

## Risks
The shared struct is a broad concurrency boundary. Field ordering is not firmware ABI, but semantic ownership is critical: locks must cover DEBI/command, PID, OSD, ioctl, and ringbuffer access consistently. Optional features must leave unused pointers safe for unregister.

## Test Signals
Compile coverage across all av7110 source files, probe allocation, tasklet/file-operation access, AV/CA/V4L register/unregister, full-TS mode, and frontend wrapper invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_av.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_av.c

## Purpose
Implements AV7110 audio/video decoder device behavior: recording/playback mode transitions, PES/TS conversion, ringbuffer feeding, video events, still-picture playback, audio/video ioctls, file operations, and AV device registration.

## Important APIs, Types, and Functions
Exports `av7110_record_cb()`, `av7110_av_start_record()`, `av7110_av_start_play()`, `av7110_av_stop()`, `av7110_pes_play()`, `av7110_set_volume()`, `av7110_set_vidmode()`, `av7110_write_to_decoder()`, `dvb_video_add_event()`, `av7110_p2t_init()`, `av7110_p2t_write()`, `av7110_av_register()`, `av7110_av_unregister()`, `av7110_av_init()`, and `av7110_av_exit()`. Internal paths parse PES headers, generate TS headers, repack TS payloads through `ipack`, and implement `VIDEO_*`/`AUDIO_*` ioctl behavior.

## Control Flow
Recording starts by stopping firmware playback, initializing PES-to-TS filters for selected demux feeds, setting `rec_mode`, and issuing firmware `__Record`. Memory playback starts by resetting ipacks, setting `playing`, and issuing firmware `__Play`. Userspace writes either TS packets or byte streams; TS is unpacked to PES via `write_ts_to_decoder()`, while byte streams are repacked by `av7110_ipack_instant_repack()`. Firmware GPIO requests later drain ringbuffers via `av7110_pes_play()`. Ioctls update software status and call firmware commands for play, stop, freeze, format, trick modes, mute, sync, mixer, and capabilities.

## State and Persistence Behavior
AV state persists in `av7110->playing`, `rec_mode`, `videostate`, `audiostate`, `trickmode`, `sinfo`, `mixer`, ringbuffers `avout`/`aout`, `ipack[]`, `p2t[]`, and video event queue. Open/release resets buffers and stops active streams as needed.

## Dependencies and Integration Points
Depends on DVB device/file APIs, ringbuffers, demux feeds, `dvb_filter_pes2ts`, firmware command helpers from `av7110_hw.c`, `ChangePIDs()` from `av7110.c`, and `av7110_ipack`.

## Risks
Ringbuffer wait paths and tasklet drains must avoid deadlocks and partial writes. PES resync and TS adaptation-field handling are sensitive to malformed input. Playback and recording are mutually exclusive through software flags, but firmware command failure can leave state partially updated. Ioctl state must stay synchronized with firmware state.

## Test Signals
Audio/video device open/write/poll/ioctl/release, demux-to-decoder TS delivery, memory playback of TS and PES streams, PES-to-TS recording, video size events, still-picture playback, trick modes, mixer volume for each ADAC type, buffer clear, and firmware-version-dependent audio capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_av.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_av.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_av.h

## Purpose
Declares the cross-file AV playback, recording, decoder, event, and registration APIs for the AV7110 driver.

## Important APIs, Types, and Functions
Exports video mode and volume setters, record/play/stop controls, PES drain/write helpers, video event insertion, PES-to-TS state helpers, and AV init/register/unregister/exit functions.

## Control Flow
The main driver and IRQ tasklets call these declarations to start firmware playback/recording, drain ringbuffers into DEBI DMA, and register DVB audio/video devices.

## State and Persistence Behavior
The APIs mutate `struct av7110` AV state, ringbuffers, ipacks, PIDs, and device pointers owned by `av7110.h`.

## Dependencies and Integration Points
Depends on `struct av7110`, `struct dvb_filter_pes2ts`, `struct dvb_demux_feed`, and video event types from included AV7110/DVB headers.

## Risks
Callers must honor playback/recording mutual exclusion and protect userspace ioctl state with the appropriate mutexes where required.

## Test Signals
Compile/link coverage from `av7110.c`, `av7110_av.c`, and tasklet paths; runtime AV device registration and playback/recording transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_av.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ca.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ca.c

## Purpose
Implements AV7110 conditional access and common-interface support, including CI message handling, link-layer ringbuffers, CA device file operations, descrambler ioctl handling, and CA device registration.

## Important APIs, Types, and Functions
Exports `CI_handle()`, `ci_get_data()`, `av7110_ca_register()`, `av7110_ca_unregister()`, `av7110_ca_init()`, and `av7110_ca_exit()`. Internal helpers are `ci_ll_init()`, `ci_ll_flush()`, `ci_ll_release()`, `ci_ll_reset()`, `ci_ll_write()`, `ci_ll_read()`, and DVB CA file operations/ioctl handlers.

## Control Flow
Firmware CI events enter through `CI_handle()` or `ci_get_data()` from the main DEBI/GPIO tasklet path. Userspace opens `/dev/dvb/.../ca*`, reads from `ci_rbuffer`, writes link-layer messages to `ci_wbuffer`, polls buffer readiness, resets slots, queries capabilities/slot/descrambler info, and sets descrambler keys through firmware `SetDescr` commands.

## State and Persistence Behavior
Per-card CI state lives in `av7110->ci_slot[]`, `ci_rbuffer`, and `ci_wbuffer`. CA open flushes both buffers. Reset enqueues reset messages and clears slot flags. Ringbuffer storage is vmalloc-backed during `av7110_ca_init()` and released on exit.

## Dependencies and Integration Points
Depends on DVB CA/device/ringbuffer APIs, `array_index_nospec()`, firmware command helpers, and the main AV7110 ioctl mutex. Firmware capability `FW_CI_LL_SUPPORT()` determines reported CA type.

## Risks
Link-layer read/write framing uses two-byte length prefixes and requires buffer-space validation. Userspace counts above 2048 are rejected. Slot indices must stay bounded; `array_index_nospec()` is used after validation. Firmware command errors from `SetDescr` are not propagated in detail inside that ioctl case.

## Test Signals
CA device register/unregister, open flush behavior, poll readiness, nonblocking read/write, reset both slots, CI module present/ready updates, CA capability/slot/descrambler queries, and setting valid/invalid descrambler keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ca.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ca.h

## Purpose
Declares the AV7110 CA/CI message, ringbuffer, and lifecycle interface.

## Important APIs, Types, and Functions
Declares `CI_handle()`, `ci_get_data()`, `av7110_ca_register()`, `av7110_ca_unregister()`, `av7110_ca_init()`, and `av7110_ca_exit()`.

## Control Flow
Main driver code initializes CA buffers and registers the DVB CA device; IRQ-side firmware event handling calls `CI_handle()` and `ci_get_data()`.

## State and Persistence Behavior
Declared APIs operate on `struct av7110` CA slots and CI ringbuffers.

## Dependencies and Integration Points
Forward-declares `struct av7110` and relies on included users to have DVB ringbuffer and integer types available through shared headers.

## Risks
Header users must include it in contexts where `struct dvb_ringbuffer`, `u8`, and `u16` are defined.

## Test Signals
Compile coverage in `av7110.c` and `av7110_ca.c`, plus runtime CA init/register/read/write/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_ca.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_hw.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_hw.c

## Purpose
Implements low-level AV7110 hardware access, ARM firmware boot/loading, DEBI command protocol, firmware request/command helpers, DiSEqC commands, and optional firmware-backed OSD operations.

## Important APIs, Types, and Functions
Exports `av7110_debiwrite()`, `av7110_debiread()`, `av7110_bootarm()`, `av7110_wait_msgstate()`, `av7110_fw_cmd()`, `av7110_fw_request()`, `av7110_firmversion()`, `av7110_diseqc_send()`, and, when OSD is enabled, `av7110_osd_cmd()` and `av7110_osd_capability()`. Internal helpers include `waitdebi()`, `load_dram()`, `__av7110_send_fw_cmd()`, `av7110_send_fw_cmd()`, `av7110_fw_query()`, OSD drawing/window wrappers, bitmap load/blit/release, palette conversion, and RGB-to-YUV conversion.

## Control Flow
`av7110_bootarm()` resets the ARM, disables IRQs, enables/tests DEBI, clears DPRAM, loads `av7110/bootcode.bin`, handshakes DRAM root image transfer in blocks via DPRAM, loads DPRAM code, raises reset, clears mailboxes, and enables GPIO IRQ. Firmware commands wait for command idle and message queue availability, write command words to DEBI command registers, and optionally read replies from `COM_BUFF`. OSD ioctls translate high-level OSD commands into firmware commands and staged bitmap/text writes.

## State and Persistence Behavior
Uses `av7110->arm_ready`, `arm_errors`, firmware version fields, `debi_bus`/`debi_virt`, `dcomlock`, and OSD bitmap state. Firmware command protocol persists in AV7110 DPRAM/command registers. Bitmap load state uses `bmp_state`, `bmplen`, `bmpp`, `bmpbuf`, and `bmpq`.

## Dependencies and Integration Points
Depends on SAA7146 DEBI registers/macros, firmware loader, AV7110 hardware register definitions from `av7110_hw.h`, wait/delay APIs, and shared `struct av7110`. Called by probe, watchdog recovery, demux/feed logic, AV/CA ioctl code, frontend SEC functions, and optional OSD device handlers.

## Risks
Hardware protocol timing is fragile: timeouts, mailbox state, command queues, and optional handshaking must match firmware versions. DEBI transfer lengths are capped and immediate/block transfer behavior differs. ARM boot depends on external bootcode and validated root/DPRAM images from `av7110.c`. OSD bitmap copying has size and firmware-version corner cases, especially around interrupted syscalls while a bitmap is loading.

## Test Signals
DEBI read/write loopback, missing bootcode handling, ARM boot/version query, firmware command timeout paths, firmware request replies, DiSEqC send, queue busy/overflow behavior, OSD window/palette/text/bitmap commands, bitmap timeout, and crash recovery reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/av7110/av7110_hw.c -->
