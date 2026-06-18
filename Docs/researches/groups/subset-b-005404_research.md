# subset-b-005404 Research

Grouped research for AtomISP CSS parameter, stream, pipe, input-system, IRQ, and early ISP kernel tuning files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_params.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_params.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_params.c` is the generated host side ISP parameter dispatch implementation in the Intel AtomISP CSS driver. It binds `IA_CSS_*_ID` parameter identifiers to `ia_css_process_*` functions, copies public `ia_css_isp_parameters` fields into binary memory parameter buffers, and exposes generated setters/getters for most public ISP filter configs.

## Important APIs, Types, and Functions

Visible functions: `ia_css_debug_dtrace`, `ia_css_anr_encode`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_anr2_vmem_encode`, `ia_css_debug_dtrace`, `ia_css_bh_encode`, `ia_css_debug_dtrace`, `ia_css_cnr_encode`, `ia_css_debug_dtrace`. Visible structs: `struct ia_css_isp_parameters *params)`, `struct sh_css_isp_aa_params *t =  (struct sh_css_isp_aa_params *)`, `struct ia_css_isp_parameters *params)`, `struct ia_css_isp_parameters *params)`, `struct ia_css_isp_parameters *params)`, `struct ia_css_isp_parameters *params)`, `struct ia_css_isp_parameters *params)`, `struct ia_css_isp_parameters *params)`, `struct ia_css_isp_parameters *params)`, `struct ia_css_isp_parameters *params)`. Visible enums: none visible in this file. Important macros/constants: `IA_CSS_INCLUDE_PARAMETERS`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

The process path receives a pipe id, pipeline stage, and parameter set. Each processor reads the stage binary's generated memory offset for its kernel, skips absent kernels when size is zero, encodes the host configuration into DMEM/VMEM/VAMEM/HMEM, and marks `isp_params_changed` plus the per-pipe/per-stage memory dirty bit.

## State and Persistence Behavior

The set/get path copies scalar/table wrapper structs between `struct ia_css_isp_config` pointers and the cached `struct ia_css_isp_parameters`. Multi-memory configs such as DVS/DVS2, NR/BNR, and S3A/BH deliberately mark several parameter ids dirty from one API update.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

State is transient host-side cache and binary memory state, not file persistence. The risk is table/index drift between generated enum order, offset structs, dispatch arrays, and firmware binary layouts; most functions trust generated size/offset data and only assert on the top-level parameter pointer.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 3335 lines, 98138 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_params.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_params.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_params.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_params.h` is the generated parameter id and memory-offset contract in the Intel AtomISP CSS driver. It defines `enum ia_css_parameter_ids`, `struct ia_css_memory_offsets`, and, when `IA_CSS_INCLUDE_PARAMETERS` is set, declarations for the process table plus generated config setters.

## Important APIs, Types, and Functions

Visible functions: `ia_css_set_dp_config`, `ia_css_set_wb_config`, `ia_css_set_tnr_config`, `ia_css_set_ob_config`, `ia_css_set_de_config`, `ia_css_set_anr_config`, `ia_css_set_anr2_config`, `ia_css_set_ce_config`, `ia_css_set_ecd_config`, `ia_css_set_ynr_config`. Visible structs: `struct ia_css_memory_offsets`, `struct`, `struct ia_css_isp_parameter aa;`, `struct ia_css_isp_parameter anr;`, `struct ia_css_isp_parameter bh;`, `struct ia_css_isp_parameter cnr;`, `struct ia_css_isp_parameter crop;`, `struct ia_css_isp_parameter csc;`, `struct ia_css_isp_parameter dp;`, `struct ia_css_isp_parameter bnr;`. Visible enums: `enum ia_css_parameter_ids`. Important macros/constants: `_IA_CSS_ISP_PARAM_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Control flow is indirect: pipeline code indexes `ia_css_kernel_process_param[id]`, and each function uses the matching member in `mem_offsets.offsets.param` to locate the kernel's parameter block in the binary memory images.

## State and Persistence Behavior

No runtime state is stored here, but the header fixes the ABI between generated binary metadata, host parameter cache, and kernel-specific encoders.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

The main risk is generated-order mismatch. Adding or reordering ids requires regenerating the process table, offset structs, and every binary metadata producer in lockstep.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 383 lines, 10960 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_states.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_states.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_states.c` is the generated ISP state initializer dispatch implementation in the Intel AtomISP CSS driver. It binds `IA_CSS_*_STATE_ID` values to init routines for AA, CNR, CNR2, DP, DE, TNR, REF, and YNR state memory.

## Important APIs, Types, and Functions

Visible functions: `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Each initializer looks up the generated state memory offset in a binary, skips zero-sized state, then either zeroes the VMEM block or calls a kernel-specific `ia_css_init_*_state` helper for DMEM/VMEM layout initialization.

## State and Persistence Behavior

The initialized memory belongs to the binary's `mem_params.params[IA_CSS_PARAM_CLASS_STATE]` buffers and persists for the life of the loaded binary/stage until reinitialized or freed with the binary.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risk centers on binary metadata validity and on stale state if callers forget to run the initializer before a stage starts. Tests should exercise binaries with present and absent state blocks.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 215 lines, 6137 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_states.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_states.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_states.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_states.h` is the generated state id and state-memory-offset contract in the Intel AtomISP CSS driver. It declares `enum ia_css_state_ids`, `struct ia_css_state_memory_offsets`, and the optional `ia_css_kernel_init_state` function pointer table.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_state_memory_offsets`, `struct`, `struct ia_css_isp_parameter aa;`, `struct ia_css_isp_parameter cnr;`, `struct ia_css_isp_parameter cnr2;`, `struct ia_css_isp_parameter dp;`, `struct ia_css_isp_parameter de;`, `struct ia_css_isp_parameter ynr;`, `struct`, `struct ia_css_isp_parameter tnr;`. Visible enums: `enum ia_css_state_ids`. Important macros/constants: `IA_CSS_INCLUDE_STATES`, `_IA_CSS_ISP_STATE_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Pipeline setup uses the enum as an index into the init table, while binary metadata supplies the actual DMEM/VMEM offsets and sizes.

## State and Persistence Behavior

The header has no storage, but it is part of the generated ABI connecting firmware binary metadata and host initialization code.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Drift between enum order, offset members, and generated init table entries can silently initialize the wrong memory block.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 65 lines, 1880 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_isp_states.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_metadata.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_metadata.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_metadata.h` is the public metadata buffer layout and allocation API in the Intel AtomISP CSS driver. It defines metadata configuration, computed metadata layout, and `struct ia_css_metadata` with CSS virtual address and exposure id.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_metadata_config`, `struct ia_css_resolution  resolution; /** Resolution */`, `struct ia_css_metadata_info`, `struct ia_css_resolution resolution; /** Resolution */`, `struct ia_css_metadata`, `struct ia_css_metadata_info info;    /** Layout info */`, `struct ia_css_metadata *`. Visible enums: `enum atomisp_input_format data_type; /** Data type of CSI-2 embedded`. Important macros/constants: `__IA_CSS_METADATA_H`, `SIZE_OF_IA_CSS_METADATA_STRUCT`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Streams use `ia_css_metadata_config` to describe embedded CSI-2 metadata, derive `ia_css_metadata_info`, then allocate/free CSS-addressed metadata buffers through `ia_css_metadata_allocate()` and `ia_css_metadata_free()`.

## State and Persistence Behavior

The struct is a host handle to CSS memory; persistence is tied to explicit allocation and free. Exposure id travels with the buffer to correlate metadata with frames.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risk is size/stride mismatch for embedded formats and lifetime mistakes around the CSS virtual address. Tests should cover embedded data formats, zero/large metadata sizes, and allocation failure.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 68 lines, 2051 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mipi.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mipi.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mipi.h` is the public MIPI frame sizing helper interface in the Intel AtomISP CSS driver. It declares `ia_css_mipi_frame_calculate_size()` for converting width, height, atomisp input format, optional SOL/EOL packets, and embedded-data words into a 32-byte-memory-word frame size.

## Important APIs, Types, and Functions

Visible functions: `ia_css_mipi_frame_calculate_size`. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_MIPI_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Callers use it before allocating buffered-sensor/MIPI capture buffers. The function is expected to validate unsupported formats and return an error code rather than writing a bogus size.

## State and Persistence Behavior

There is no persistent state. The output size feeds later buffer allocation and DMA programming.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are integer overflow, off-by-one packing for RAW/compressed formats, and confusion between bytes, pixels, and 32-byte memory words.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 39 lines, 1213 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mipi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mmu.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mmu.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mmu.h` is the public CSS MMU cache invalidation hook in the Intel AtomISP CSS driver. It declares `ia_css_mmu_invalidate_cache()`, used after CSS page-table changes so the ISP-side translation cache does not retain stale mappings.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_MMU_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Control flow is a direct hardware side effect: memory management code updates page tables, then calls this hook before firmware/ISP accesses the new mappings.

## State and Persistence Behavior

State lives in CSS MMU hardware TLB/cache, not this header. Missing invalidation can produce DMA to stale physical pages.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Tests should cover remap/unmap/reuse paths and power-management paths that rebuild page tables.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 24 lines, 614 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mmu_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mmu_private.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mmu_private.h` is the private MMU page-table base programming interface in the Intel AtomISP CSS driver. It declares `sh_css_mmu_set_page_table_base_index(hrt_data base_index)`, a lower-level setup hook for programming the L1 page-table base after ISP power-up.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_MMU_PRIVATE_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

The intended flow is early CSS/MMU initialization: set the L1 base once, then rely on protection against later modification.

## State and Persistence Behavior

The persistent state is hardware configuration, so ordering relative to power-up and MMU cache invalidation is critical.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include treating an index as a byte address on platforms where `l1_base_is_index` differs, and attempting to reprogram after the hardware protects the base.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 21 lines, 526 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mmu_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_morph.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_morph.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_morph.h` is the morph table allocation API for GDC/lens correction in the Intel AtomISP CSS driver. It declares allocation and free helpers for `struct ia_css_morph_table`, whose full layout in `ia_css_types.h` carries six planes of X/Y coordinate arrays.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_morph_table *`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_MORPH_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Callers allocate by grid width/height, fill coordinate planes, pass the table through ISP config, and free it when no pipe references it.

## State and Persistence Behavior

The table memory is host-owned, and `ia_css_isp_config` comments say morph tables are pointer-copied rather than deep-copied, so caller lifetime matters.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Tests should cover allocation failure, zero dimensions, all six planes, and freeing after stream/pipe teardown.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 31 lines, 741 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_morph.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe.h` is the private CSS pipe runtime state definition in the Intel AtomISP CSS driver. It defines mode-specific pipe settings for preview, video, capture, and YUV post-processing plus the central `struct ia_css_pipe` with public config/info, binaries, frames, continuous buffers, metadata buffers, pipeline, stream backpointer, and pipe number.

## Important APIs, Types, and Functions

Visible functions: `sh_css_param_update_isp_params`. Visible structs: `struct ia_css_preview_settings`, `struct ia_css_binary copy_binary;`, `struct ia_css_binary preview_binary;`, `struct ia_css_binary vf_pp_binary;`, `struct ia_css_frame *delay_frames[MAX_NUM_VIDEO_DELAY_FRAMES];`, `struct ia_css_frame *tnr_frames[NUM_VIDEO_TNR_FRAMES];`, `struct ia_css_pipe *copy_pipe;`, `struct ia_css_pipe *capture_pipe;`, `struct ia_css_capture_settings`, `struct ia_css_binary copy_binary;`. Visible enums: `enum ia_css_pipe_id		mode;`. Important macros/constants: `__IA_CSS_PIPE_H__`, `PIPE_ENTRY_EMPTY_TOKEN`, `PIPE_ENTRY_RESERVED_TOKEN`, `IA_CSS_DEFAULT_PREVIEW_SETTINGS`, `IA_CSS_DEFAULT_CAPTURE_SETTINGS`, `IA_CSS_DEFAULT_VIDEO_SETTINGS`, `IA_CSS_DEFAULT_YUVPP_SETTINGS`, `IA_CSS_DEFAULT_PIPE`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Control flow starts from public pipe creation, fills this private structure, maps queues, builds binary pipelines, updates ISP params through `sh_css_param_update_isp_params()`, and links the pipe into streams.

## State and Persistence Behavior

State is long-lived per pipe: selected binaries, owned frame structures, continuous capture frames, metadata buffers, shading/scaler resources, and SP thread mapping token.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are lifecycle leaks across mode-specific unions, stale pipe numbers, and accidental use of uninitialized union members when pipe mode changes.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 173 lines, 5957 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe_public.h` is the public CSS pipe API and configuration contract in the Intel AtomISP CSS driver. It exposes pipe modes, pipe versions, `struct ia_css_pipe_config`, `struct ia_css_pipe_info`, and APIs to create/destroy pipes, query info, set ISP config, manage event IRQ masks, enqueue/dequeue buffers, set scaler LUTs, and override output formats.

## Important APIs, Types, and Functions

Visible functions: `ia_css_pipe_create`, `ia_css_pipe_get_info`, `ia_css_pipe_set_isp_config`, `ia_css_pipe_set_irq_mask`, `ia_css_pipe_set_irq_mask`, `ia_css_pipe_set_irq_mask`, `ia_css_pipe_set_irq_mask`, `ia_css_pipe_set_irq_mask`, `ia_css_pipe_set_irq_mask`, `ia_css_event_get_irq_mask`. Visible structs: `struct ia_css_pipe_config`, `struct ia_css_resolution input_effective_res;`, `struct ia_css_resolution bayer_ds_out_res;`, `struct ia_css_resolution capt_pp_in_res;`, `struct ia_css_resolution vf_pp_in_res;`, `struct ia_css_resolution output_system_in_res;`, `struct ia_css_resolution dvs_crop_out_res;`, `struct ia_css_frame_info output_info[IA_CSS_PIPE_MAX_OUTPUT_STAGE];`, `struct ia_css_frame_info vf_output_info[IA_CSS_PIPE_MAX_OUTPUT_STAGE];`, `struct ia_css_capture_config default_capture_config;`. Visible enums: `enum`, `enum ia_css_pipe_mode`, `enum ia_css_pipe_version`, `enum ia_css_pipe_mode mode;`, `enum ia_css_pipe_version isp_pipe_version;`, `enum ia_css_frame_delay dvs_frame_delay;`, `enum ia_css_frame_format format);`. Important macros/constants: `__IA_CSS_PIPE_PUBLIC_H`, `IA_CSS_PIPE_MODE_NUM`, `DEFAULT_PIPE_CONFIG`, `DEFAULT_PIPE_INFO`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

The typical flow is defaults, fill mode/resolutions/output formats, create pipe, attach to a stream, optionally set ISP/filter config or IRQ masks, then queue/dequeue buffers while streaming.

## State and Persistence Behavior

Pipe state persists in the created pipe object and in firmware/SP queues after stream start. Some config pointers are copied, while table pointers such as shading/morph are not deeply copied according to `ia_css_types.h`.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include invalid resolution combinations, calling override/scaler APIs after stream start, mismatched output pin indexes, and buffer ownership mistakes after enqueue.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 464 lines, 17399 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_pipe_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_prbs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_prbs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_prbs.h` is the deprecated PRBS test input configuration contract in the Intel AtomISP CSS driver. It defines PRBS ids and `struct ia_css_prbs_config` with blanking and two seed values for pseudo-random input generation.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_prbs_config`. Visible enums: `enum ia_css_prbs_id`, `enum ia_css_prbs_id	id;`. Important macros/constants: `__IA_CSS_PRBS_H`, `N_CSS_PRBS_IDS`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Streams select `IA_CSS_INPUT_MODE_PRBS` and place this config in the stream source union; lower input-system code programs the generator.

## State and Persistence Behavior

State is test-generator hardware state seeded from this struct.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are stale deprecated API use and seed/blanking combinations that do not match expected frame dimensions.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 45 lines, 1129 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_prbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_properties.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_properties.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_properties.h` is the CSS hardware property query interface in the Intel AtomISP CSS driver. It defines `struct ia_css_properties` containing GDC coordinate scale, whether the L1 MMU base is an index, and the VAMEM type, plus `ia_css_get_properties()`.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_properties`. Visible enums: `enum ia_css_vamem_type vamem_type;`. Important macros/constants: `__IA_CSS_PROPERTIES_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Callers query once during setup or capability reporting and branch on returned hardware constants.

## State and Persistence Behavior

The state is a snapshot of compiled/platform hardware properties.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are stale property values when supporting multiple ISP generations and misuse of MMU base semantics.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 33 lines, 857 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_properties.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_shading.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_shading.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_shading.h` is the shading table allocation API in the Intel AtomISP CSS driver. It declares `ia_css_shading_table_alloc()` and `ia_css_shading_table_free()` for lens shading correction tables described by `ia_css_shading_info` in `ia_css_types.h`.

## Important APIs, Types, and Functions

Visible functions: `ia_css_shading_table_alloc`. Visible structs: `struct ia_css_shading_table *`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_SHADING_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Callers allocate a table sized to CSS-reported shading grid info, fill per-color gains, attach it through ISP config, and retain it while the pipe can use it.

## State and Persistence Behavior

The memory is host-owned and referenced by pointer from config/pipe code rather than always deep-copied.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Tests should cover grid dimensions from pipe info, null frees, allocation failure, and stream teardown with active shading tables.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 32 lines, 776 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_shading.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream.h` is the private CSS stream runtime state definition in the Intel AtomISP CSS driver. It defines `struct ia_css_stream`, storing public stream config/info, RX configuration, pipe list, continuous-pipe pointers, ISP parameter caches, continuous capture flags, stop/start state, and testing/helper APIs.

## Important APIs, Types, and Functions

Visible functions: `sh_css_params_set_binning_factor`, `ia_css_get_isp_dis_coefficients`, `ia_css_get_isp_dvs2_coefficients`. Visible structs: `struct ia_css_stream`, `struct ia_css_stream_config    config;`, `struct ia_css_stream_info      info;`, `struct ia_css_pipe            *last_pipe;`, `struct ia_css_pipe           **pipes;`, `struct ia_css_pipe            *continuous_pipe;`, `struct ia_css_isp_parameters  *isp_params_configs;`, `struct ia_css_isp_parameters  *per_frame_isp_params_configs;`, `struct ia_css_binary *`, `struct ia_css_binary *`. Visible enums: none visible in this file. Important macros/constants: `_IA_CSS_STREAM_H_`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Public stream creation fills this private object, links pipes, computes RX/input settings, initializes ISP parameter caches, and later start/stop updates firmware/SP pipeline state.

## State and Persistence Behavior

State persists for the stream lifetime and includes per-frame ISP parameter caches and continuous capture flags that affect raw buffer management.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include stale `last_pipe`, mismatched `num_pipes` and `pipes`, parameter cache invalidation errors, and stop/start state races.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 99 lines, 2823 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream_format.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream_format.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream_format.h` is the input-format bits-per-pixel utility declaration in the Intel AtomISP CSS driver. It declares `ia_css_util_input_format_bpp()` for mapping atomisp input formats and two-pixels-per-clock mode to a packed bit depth.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: `enum atomisp_input_format format,`. Important macros/constants: `__IA_CSS_STREAM_FORMAT_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Sizing code calls this from stream/MIPI setup to calculate line stride and buffer requirements.

## State and Persistence Behavior

No state is stored here.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are ABI format enum drift and wrong RAW/compressed bit depth in two-PPC mode.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 21 lines, 512 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream_public.h` is the public CSS stream API and input configuration contract in the Intel AtomISP CSS driver. It defines input modes, MIPI buffer config, ISYS stream configs, `struct ia_css_stream_config`, stream info, and APIs to create/destroy/start/stop streams, manage continuous capture, query formats, and inject FIFO test frames.

## Important APIs, Types, and Functions

Visible functions: `ia_css_stream_create`, `ia_css_stream_get_info`, `ia_css_stream_set_output_padded_width`, `ia_css_stream_get_max_buffer_depth`, `ia_css_stream_capture`, `ia_css_stream_capture_frame`, `ia_css_stream_send_input_frame`, `ia_css_stream_send_input_line`, `ia_css_stream_send_input_embedded_line`, `ia_css_stream_set_isp_config_on_pipe`. Visible structs: `struct ia_css_mipi_buffer_config`, `struct ia_css_stream_isys_stream_config`, `struct ia_css_resolution  input_res; /** Resolution of input data */`, `struct ia_css_stream_input_config`, `struct ia_css_resolution  input_res; /** Resolution of input data */`, `struct ia_css_resolution  effective_res; /** Resolution of input data.`, `struct ia_css_stream_config`, `struct ia_css_input_port  port; /** Port, for sensor only. */`, `struct ia_css_prbs_config prbs; /** PRBS configuration */`, `struct ia_css_stream_isys_stream_config`. Visible enums: `enum ia_css_input_mode`, `enum`, `enum atomisp_input_format format; /** Format of input stream. This data`, `enum atomisp_input_format format; /** Format of input stream. This data`, `enum ia_css_bayer_order bayer_order; /** Bayer order for RAW streams */`, `enum ia_css_input_mode    mode; /** Input mode */`, `enum atomisp_input_format`, `enum atomisp_input_format format,`. Important macros/constants: `__IA_CSS_STREAM_PUBLIC_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

The common flow is default config, fill sensor/FIFO/TPG/PRBS/memory input details, create a stream from one or more pipes, start it, queue pipe buffers, capture or stop as needed, then destroy/unload.

## State and Persistence Behavior

State persists in the stream object and firmware queues. Continuous capture settings drive raw buffer allocation/depth, metadata layout, and raw buffer locking.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include invalid channel ids, inconsistent effective/input resolutions, continuous buffer depth underallocation, and using test FIFO injection APIs with mismatched format/two-PPC values.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 553 lines, 19917 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_stream_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_timer.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_timer.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_timer.h` is the CSS timer measurement ABI in the Intel AtomISP CSS driver. It defines tick types, timer event ids, `struct ia_css_clock_tick`, `struct ia_css_time_meas`, size macros, and `ia_css_timer_get_current_tick()`.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_clock_tick`, `struct ia_css_time_meas`, `struct ia_css_clock_tick *curr_ts);`. Visible enums: `enum ia_css_tm_event`. Important macros/constants: `__IA_CSS_TIMER_H`, `SIZE_OF_IA_CSS_CLOCK_TICK_STRUCT`, `SIZE_OF_IA_CSS_TIME_MEAS_STRUCT`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Code can capture start/end clock ticks around driver, CSS, or ISP events and compute elapsed cycles outside this header.

## State and Persistence Behavior

State is either returned current hardware tick or caller-owned measurement structs.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are tick wraparound, struct size assumptions shared with firmware, and event id drift.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 61 lines, 1727 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_types.h` is the central public CSS data-type and ISP configuration header in the Intel AtomISP CSS driver. It defines core scalar types, resolutions, coordinates, data handles, shading/grid/morph/DVS/zoom/capture structures, and the large `struct ia_css_isp_config` pointer bundle for ISP filter settings.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_isp_parameters;`, `struct ia_css_pipe;`, `struct ia_css_memory_offsets;`, `struct ia_css_config_memory_offsets;`, `struct ia_css_state_memory_offsets;`, `struct ia_css_resolution`, `struct ia_css_coordinate`, `struct ia_css_vector`, `struct ia_css_data`, `struct ia_css_host_data`. Visible enums: `enum ia_css_shading_correction_type`, `enum ia_css_shading_correction_type type; /** Shading Correction type. */`, `enum ia_css_vamem_type vamem_type;`, `enum ia_css_capture_mode`, `enum ia_css_capture_mode mode; /** Still capture mode */`. Important macros/constants: `_IA_CSS_TYPES_H`, `IA_CSS_DVS_STAT_GRID_INFO_SUPPORTED`, `IA_CSS_VERSION_MAJOR`, `IA_CSS_VERSION_MINOR`, `IA_CSS_VERSION_REVISION`, `IA_CSS_MORPH_TABLE_NUM_PLANES`, `IA_CSS_ISYS_MIN_EXPOSURE_ID`, `IA_CSS_ISYS_MAX_EXPOSURE_ID`, `SIZE_OF_IA_CSS_PTR`, `IA_CSS_ISP_DMEM`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Most public pipe and stream APIs include this header; parameter setters copy pointed-to config structs into `ia_css_isp_parameters`, while shading and morph tables are documented as pointer-copied.

## State and Persistence Behavior

State is caller-owned unless copied by a setter. Tables and buffers referenced by pointer need explicit lifetime management across pipe/stream use.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are ABI drift, shallow pointer lifetime bugs, default macro omissions, and coordinate normalization regressions across digital zoom, DVS, shading, and face/3A windows.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 596 lines, 24146 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_version.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_version.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_version.h` is the CSS API version retrieval declaration in the Intel AtomISP CSS driver. It defines `MAX_VERSION_SIZE` and declares `ia_css_get_version()` for composing the current CSS API string, optionally including firmware version when loaded.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_VERSION_H`, `MAX_VERSION_SIZE`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Callers provide an output buffer and maximum size; the implementation should return an error if the composed string does not fit.

## State and Persistence Behavior

No persistent state is stored in the header, but the result depends on linked version data and loaded firmware state.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Tests should cover null buffers, small buffers, and loaded/unloaded firmware cases.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 32 lines, 886 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_version_data.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_version_data.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_version_data.h` is the generated CSS release string data in the Intel AtomISP CSS driver. It defines `ISP2400_CSS_VERSION_STRING` and `ISP2401_CSS_VERSION_STRING` with release, API, git, SDK, and user metadata.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_VERSION_DATA_H`, `ISP2400_CSS_VERSION_STRING`, `ISP2401_CSS_VERSION_STRING`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Version composition code selects one of these strings based on target ISP generation.

## State and Persistence Behavior

The values are compile-time constants, not runtime state.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are stale generated metadata and accidental changes to release strings used for diagnostics.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 19 lines, 770 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_version_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/if_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/if_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/if_defs.h` is the input formatter request token constants in the Intel AtomISP CSS driver. It defines request token base values for frame, line, and vector requests.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_IF_DEFS_H`, `HIVE_IF_FRAME_REQUEST`, `HIVE_IF_LINES_REQUEST`, `HIVE_IF_VECTORS_REQUEST`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Input formatter and firmware code use these constants when interpreting or issuing HIVE input formatter requests.

## State and Persistence Behavior

No state is stored here.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are magic-number drift against firmware definitions and insufficient type safety around token construction.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 14 lines, 336 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/if_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_formatter_subsystem_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_formatter_subsystem_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_formatter_subsystem_defs.h` is the input formatter subsystem register and IRQ bit definitions in the Intel AtomISP CSS driver. It maps input-switch LUT, fsync, soft-reset, channel/format, and IRQ bit ids for the IFMT GP-register block.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_if_subsystem_defs_h__`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_0`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_1`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_2`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_3`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_4`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_5`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_6`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_LUT_REG_7`, `HIVE_IFMT_GP_REGS_INPUT_SWITCH_FSYNC_LUT_REG`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Low-level input formatter code writes these register indexes to route CSI channels/formats and reset IFMT subblocks.

## State and Persistence Behavior

State lives in MMIO registers addressed by these constants.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are off-by-one register indexes and mismatched reset bits across ISP generations.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 45 lines, 2080 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_formatter_subsystem_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_selector_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_selector_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_selector_defs.h` is the input selector GP-register and IRQ definition header in the Intel AtomISP CSS driver. It defines bit widths and register indexes for sync generator, PRBS, TPG, channel id, format type, data/sideband/sync selection, soft reset, counters, and input-selector IRQs.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_input_selector_defs_h`, `HIVE_ISP_ISEL_SEL_BITS`, `HIVE_ISP_CH_ID_BITS`, `HIVE_ISP_FMT_TYPE_BITS`, `HIVE_ISEL_GP_REGS_SYNCGEN_ENABLE_IDX`, `HIVE_ISEL_GP_REGS_SYNCGEN_FREE_RUNNING_IDX`, `HIVE_ISEL_GP_REGS_SYNCGEN_PAUSE_IDX`, `HIVE_ISEL_GP_REGS_SYNCGEN_NR_FRAMES_IDX`, `HIVE_ISEL_GP_REGS_SYNCGEN_NR_PIX_IDX`, `HIVE_ISEL_GP_REGS_SYNCGEN_NR_LINES_IDX`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Input setup code programs these registers when selecting FIFO, TPG, PRBS, or sensor-like generated input.

## State and Persistence Behavior

State is hardware register content.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include width truncation for channel/format fields and stale counter/IRQ assumptions.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 80 lines, 3786 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_selector_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_switch_2400_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_switch_2400_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_switch_2400_defs.h` is the ISP2400 input-switch LUT helper and selection constants in the Intel AtomISP CSS driver. It provides macros to compute LUT register id and bit shift from channel id and MIPI format type, plus scalar/vector route selectors.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_input_switch_2400_defs_h`, `_HIVE_INPUT_SWITCH_GET_LUT_REG_ID`, `_HIVE_INPUT_SWITCH_GET_LUT_REG_LSB`, `HIVE_INPUT_SWITCH_SELECT_NO_OUTPUT`, `HIVE_INPUT_SWITCH_SELECT_IF_PRIM`, `HIVE_INPUT_SWITCH_SELECT_IF_SEC`, `HIVE_INPUT_SWITCH_SELECT_STR_TO_MEM`, `HIVE_INPUT_SWITCH_VSELECT_NO_OUTPUT`, `HIVE_INPUT_SWITCH_VSELECT_IF_PRIM`, `HIVE_INPUT_SWITCH_VSELECT_IF_SEC`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Input routing code uses these macros to steer streams to primary IF, secondary IF, stream-to-memory, or no output.

## State and Persistence Behavior

State is the programmed input-switch LUT.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are invalid channel/format values and confusion between scalar and vector route encodings.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 22 lines, 806 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_switch_2400_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_ctrl_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_ctrl_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_ctrl_defs.h` is the input-system controller register, reset, width, token, and acknowledge ABI in the Intel AtomISP CSS driver. It defines 23 controller registers, reset values, field widths, command token ids, acknowledge token ids, bit positions, port ids, and no-ack sentinel values for capture/acquisition/DMA control.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_input_system_ctrl_defs_h`, `_INPUT_SYSTEM_CTRL_REG_ALIGN`, `ISYS_CTRL_NOF_REGS`, `ISYS_CTRL_CAPT_START_ADDR_A_REG_ID`, `ISYS_CTRL_CAPT_START_ADDR_B_REG_ID`, `ISYS_CTRL_CAPT_START_ADDR_C_REG_ID`, `ISYS_CTRL_CAPT_MEM_REGION_SIZE_A_REG_ID`, `ISYS_CTRL_CAPT_MEM_REGION_SIZE_B_REG_ID`, `ISYS_CTRL_CAPT_MEM_REGION_SIZE_C_REG_ID`, `ISYS_CTRL_CAPT_NUM_MEM_REGIONS_A_REG_ID`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Input-system code writes command tokens through NEXT/LAST command registers and observes acknowledge registers/FSM state to coordinate capture frame acquisition, external capture, acquisition reads, and overrule commands.

## State and Persistence Behavior

State persists in input-system control MMIO and FSMs.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are token bitfield packing errors, assuming reset values after partial reset, and failing to handle no-ack/device-error tokens.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 235 lines, 9979 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_ctrl_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_defs.h` is the top-level input-system GP-register, reset, interrupt, stream-monitor, and DMA constants in the Intel AtomISP CSS driver. It maps multicast/mux registers, streaming monitor registers, soft-reset bit ids for capture/acquisition/DMA/CIO blocks, IRQ bit ids, and fixed DMA shape constants.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_input_system_defs_h`, `HIVE_CSI_CONFIG_MAIN`, `HIVE_CSI_CONFIG_STEREO1`, `HIVE_CSI_CONFIG_STEREO2`, `HIVE_ISYS_GPREG_MULTICAST_A_IDX`, `HIVE_ISYS_GPREG_MULTICAST_B_IDX`, `HIVE_ISYS_GPREG_MULTICAST_C_IDX`, `HIVE_ISYS_GPREG_MUX_IDX`, `HIVE_ISYS_GPREG_STRMON_STAT_IDX`, `HIVE_ISYS_GPREG_STRMON_COND_IDX`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Input-system initialization and error handling use these values to reset subblocks, choose routes, monitor streams, and interpret interrupts.

## State and Persistence Behavior

State is hardware register and IRQ controller state.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are generation mismatch and reset ordering mistakes that leave capture or DMA subblocks wedged.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 118 lines, 5273 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_global.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_global.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_global.h` is the shared input-system error namespace and generation include point in the Intel AtomISP CSS driver. It defines `input_system_err_t` values spanning ISP2401 and ISP2400 failures, then includes generation-specific global headers.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `__INPUT_SYSTEM_GLOBAL_H_INCLUDED__`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Higher-level input-system APIs return these errors while generation-specific code supplies concrete object types.

## State and Persistence Behavior

No runtime state is stored here.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are ambiguous `GENERIC` errors and enum extension without caller mapping updates.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 30 lines, 902 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_global.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_local.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_local.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_local.h` is the shared local input-system configuration type layer in the Intel AtomISP CSS driver. It defines CSI ports, network/control/channel/backend/switch config types, source config union, RX modes, compressor/predictor enums, and `rx_cfg_t`, then includes generation-specific local headers.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ctrl_unit_cfg_s`, `struct input_system_network_cfg_s`, `struct input_switch_cfg_channel_s`, `struct backend_channel_cfg_s`, `struct input_switch_cfg_s`, `struct rx_cfg_s`. Visible enums: `enum mipi_compressor`, `enum mipi_port_id		port;	/* The port ID to apply the control on */`. Important macros/constants: `UNCOMPRESSED_BITS_PER_PIXEL_10`, `UNCOMPRESSED_BITS_PER_PIXEL_12`, `COMPRESSED_BITS_PER_PIXEL_6`, `COMPRESSED_BITS_PER_PIXEL_7`, `COMPRESSED_BITS_PER_PIXEL_8`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Stream setup maps public stream input settings into these local configs before programming ISP2400/2401 input hardware.

## State and Persistence Behavior

State is caller-owned configuration passed to input-system setup code.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include invalid RX mode selection, using backward-compatible compression fields incorrectly, and mismatched two-PPC settings.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 142 lines, 3548 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_private.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_private.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_private.h` is the private generation-specific input-system include aggregator in the Intel AtomISP CSS driver. It includes ISP2401 and ISP2400 private input-system headers, exposing implementation-only internals to selected C files.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Control flow is compile-time inclusion, not runtime dispatch.

## State and Persistence Behavior

No state is declared directly here.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are namespace collisions and accidental exposure of private generation-specific definitions.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 8 lines, 241 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_public.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_public.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_public.h` is the public generation-specific input-system include aggregator in the Intel AtomISP CSS driver. It currently includes the ISP2400 public input-system API header.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Public users include this file to avoid directly selecting the generation-specific path.

## State and Persistence Behavior

No state is stored here.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are asymmetric generation coverage and accidental dependency on ISP2400-only public definitions.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 7 lines, 198 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/input_system_public.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_controller_defs.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_controller_defs.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_controller_defs.h` is the generic HRT IRQ-controller register index header in the Intel AtomISP CSS driver. It defines register indexes for edge, mask, status, clear, enable, edge-not-pulse, stream-output-enable, and register alignment.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_irq_controller_defs_h`, `_HRT_IRQ_CONTROLLER_EDGE_REG_IDX`, `_HRT_IRQ_CONTROLLER_MASK_REG_IDX`, `_HRT_IRQ_CONTROLLER_STATUS_REG_IDX`, `_HRT_IRQ_CONTROLLER_CLEAR_REG_IDX`, `_HRT_IRQ_CONTROLLER_ENABLE_REG_IDX`, `_HRT_IRQ_CONTROLLER_EDGE_NOT_PULSE_REG_IDX`, `_HRT_IRQ_CONTROLLER_STR_OUT_ENABLE_REG_IDX`, `_HRT_IRQ_CONTROLLER_REG_ALIGN`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Low-level IRQ controller helpers use these indexes to read status, mask/unmask, clear, and configure edge behavior.

## State and Persistence Behavior

State lives in IRQ-controller MMIO registers.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks include writing the wrong register index and failing to preserve mask/edge state across reset.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 20 lines, 652 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_controller_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_types_hrt.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_types_hrt.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_types_hrt.h` is the HRT CSS interrupt id and status type header in the Intel AtomISP CSS driver. It maps CSS interrupt enum values to system-defined GPIO, SP, ISP, ISYS, ISEL, IFMT, stream monitor, memory error, timer, software pin, and DMA bit ids, and defines IRQ handling status values.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `_HIVE_ISP_CSS_IRQ_TYPES_HRT_H_`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

HRT IRQ helpers and dispatchers use `hrt_isp_css_irq_t` ids to address interrupt-controller bits and return `hrt_isp_css_irq_status_t` while draining pending sources.

## State and Persistence Behavior

State is external interrupt-controller status.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are dependency on `HIVE_GP_DEV_IRQ_*` macros and enum drift when hardware interrupt sources change.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 60 lines, 3201 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/irq_types_hrt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2.host.c` is AA2 host defaults for the AtomISP CSS kernel host layer. defines `default_aa_config` and `default_baa_config`, both with strength 8191 despite comments saying default should be 0.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

defines `default_aa_config` and `default_baa_config`, both with strength 8191 despite comments saying default should be 0. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

These constants seed YUV AA and Bayer AA config before generated parameter code copies strength into `sh_css_isp_aa_params`. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 23 lines, 532 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2.host.h` is AA2 host declarations for the AtomISP CSS kernel host layer. exports the two default AA config constants.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_AA_HOST_H`.

exports the two default AA config constants. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

It is included by generated params code and public config setup code. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 19 lines, 483 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2_param.h` is AA2 ISP parameter layout for the AtomISP CSS kernel host layer. defines `struct sh_css_isp_aa_params` with signed strength.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct sh_css_isp_aa_params`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_AA_PARAM_H`.

defines `struct sh_css_isp_aa_params` with signed strength. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

The generated AA processor writes this DMEM layout directly. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 16 lines, 306 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2_types.h` is AA2 public config type for the AtomISP CSS kernel host layer. defines `struct ia_css_aa_config` with u0.13 strength.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_aa_config`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_AA2_TYPES_H`.

defines `struct ia_css_aa_config` with u0.13 strength. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

It is used for both YUV anti-aliasing and Bayer anti-aliasing. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 38 lines, 867 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/aa/aa_2/ia_css_aa2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr.host.c` is ANR v1 host encoder for the AtomISP CSS kernel host layer. defines `default_anr_config`, encodes only `threshold` into DMEM, and traces/dumps that value.

## Important APIs, Types, and Functions

Visible functions: `ia_css_debug_dtrace`, `ia_css_debug_dtrace`. Visible structs: `struct sh_css_isp_anr_params *to,`. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

defines `default_anr_config`, encodes only `threshold` into DMEM, and traces/dumps that value. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

The larger thresholds/factors arrays are public config data but this encoder ignores them for the visible DMEM layout. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 53 lines, 1157 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr.host.h` is ANR v1 host declarations for the AtomISP CSS kernel host layer. exports `default_anr_config`, encode, dump, and debug trace functions.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct sh_css_isp_anr_params *to,`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_ANR_HOST_H`.

exports `default_anr_config`, encode, dump, and debug trace functions. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

Generated parameter code calls `ia_css_anr_encode()` for ANR DMEM blocks. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 31 lines, 669 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr_param.h` is ANR v1 ISP parameter layout for the AtomISP CSS kernel host layer. defines `struct sh_css_isp_anr_params` with `threshold`.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct sh_css_isp_anr_params`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_ANR_PARAM_H`.

defines `struct sh_css_isp_anr_params` with `threshold`. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

Firmware-visible state is a compact DMEM threshold. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 17 lines, 348 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr_types.h` is ANR v1 public config type for the AtomISP CSS kernel host layer. defines DMA bit constants and `struct ia_css_anr_config` with threshold, 64 thresholds, and 3 factors.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_anr_config`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_ANR_TYPES_H`, `ANR_BPP`, `ANR_ELEMENT_BITS`.

defines DMA bit constants and `struct ia_css_anr_config` with threshold, 64 thresholds, and 3 factors. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

Only a subset is consumed by the visible host encoder. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 29 lines, 657 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_1.0/ia_css_anr_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2.host.c` is ANR2 host VMEM encoder for the AtomISP CSS kernel host layer. copies `ia_css_anr_thres.data` into `ia_css_isp_anr2_params.data` by `ANR_PARAM_SIZE` rows and `ISP_VEC_NELEMS` columns.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_isp_anr2_params *to,`. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

copies `ia_css_anr_thres.data` into `ia_css_isp_anr2_params.data` by `ANR_PARAM_SIZE` rows and `ISP_VEC_NELEMS` columns. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

It ignores `size` and has a no-op debug trace. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 38 lines, 703 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2.host.h` is ANR2 host declarations for the AtomISP CSS kernel host layer. declares the VMEM encoder and debug trace and includes the default threshold table declaration.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_isp_anr2_params *to,`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_ANR2_HOST_H`.

declares the VMEM encoder and debug trace and includes the default threshold table declaration. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

Generated parameter code calls the VMEM encoder for ANR2 offsets. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 27 lines, 586 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_param.h` is ANR2 ISP VMEM parameter layout for the AtomISP CSS kernel host layer. defines `struct ia_css_isp_anr2_params` as a VMEM array of `ANR_PARAM_SIZE * ISP_VEC_NELEMS`.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_isp_anr2_params`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_ANR2_PARAM_H`.

defines `struct ia_css_isp_anr2_params` as a VMEM array of `ANR_PARAM_SIZE * ISP_VEC_NELEMS`. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

The layout must match vector width and firmware expectations. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 19 lines, 423 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_table.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_table.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_table.host.c` is ANR2 default threshold table for the AtomISP CSS kernel host layer. defines `default_anr_thres` as a large 13 by 64 threshold data array under the active `#if 1` branch.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

defines `default_anr_thres` as a large 13 by 64 threshold data array under the active `#if 1` branch. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

It is static tuning data compiled into the host driver. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 47 lines, 6438 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_table.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_table.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_table.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_table.host.h` is ANR2 default table declaration for the AtomISP CSS kernel host layer. exports `default_anr_thres`.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_ANR2_TABLE_HOST_H`.

exports `default_anr_thres`. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

Default config setup includes this header to seed ANR2 tuning. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 14 lines, 340 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_table.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_types.h` is ANR2 public threshold type for the AtomISP CSS kernel host layer. defines `ANR_PARAM_SIZE` and `struct ia_css_anr_thres` with `s16 data[13 * 64]`.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_anr_thres`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_ANR2_TYPES_H`, `ANR_PARAM_SIZE`.

defines `ANR_PARAM_SIZE` and `struct ia_css_anr_thres` with `s16 data[13 * 64]`. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

The size is assumed by VMEM encoding loops. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 23 lines, 471 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/anr/anr_2/ia_css_anr2_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh.host.c` is BH host encoder/decoder for the AtomISP CSS kernel host layer. decodes interleaved HMEM histogram bins into `ia_css_3a_rgby_output` and encodes 3A AE Y coefficients into DMEM with fixed-point fitting.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_3a_rgby_output *out_ptr,`, `struct sh_css_isp_bh_params *to,`. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

decodes interleaved HMEM histogram bins into `ia_css_3a_rgby_output` and encodes 3A AE Y coefficients into DMEM with fixed-point fitting. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

It asserts HMEM size and depends on `ISP_HIST_*` dimensions. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 55 lines, 1343 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh.host.h` is BH host declarations for the AtomISP CSS kernel host layer. declares histogram decode and parameter encode helpers.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_3a_rgby_output *out_ptr,`, `struct sh_css_isp_bh_params *to,`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_BH_HOST_H`.

declares histogram decode and parameter encode helpers. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

Generated params code marks BH DMEM/HMEM dirty and calls the encode helper. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 24 lines, 542 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh_param.h` is BH ISP parameter layouts for the AtomISP CSS kernel host layer. defines DMEM Y coefficients and an HMEM histogram table wrapper.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct sh_css_isp_bh_params`, `struct sh_css_isp_bh_hmem_params`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_HB_PARAM_H`, `__INLINE_HMEM__`.

defines DMEM Y coefficients and an HMEM histogram table wrapper. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

These layouts bridge 3A config and histogram output memory. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 32 lines, 661 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh_types.h` is BH table type and color indexes for the AtomISP CSS kernel host layer. defines BH table size/unit size, R/G/B/Y indexes, and `struct ia_css_bh_table`.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_bh_table`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_BH_TYPES_H`, `IA_CSS_HMEM_BH_TABLE_SIZE`, `IA_CSS_HMEM_BH_UNIT_SIZE`, `BH_COLOR_R`, `BH_COLOR_G`, `BH_COLOR_B`, `BH_COLOR_Y`, `BH_COLOR_NUM`.

defines BH table size/unit size, R/G/B/Y indexes, and `struct ia_css_bh_table`. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

Decode code relies on these dimensions matching `hmem.h`. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 27 lines, 653 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bh/bh_2/ia_css_bh_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm.host.c` is BNLM host encoders for the AtomISP CSS kernel host layer. builds replicated VMEM LUT blocks, fixed division/intercept/power tables, and DMEM scalar fields for Bayer Non-Linear Mean denoise.

## Important APIs, Types, and Functions

Visible functions: `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`. Visible structs: `struct bnlm_vmem_params *to,`, `struct bnlm_dmem_params *to,`. Visible enums: none visible in this file. Important macros/constants: `BNLM_DIV_LUT_SIZE`.

builds replicated VMEM LUT blocks, fixed division/intercept/power tables, and DMEM scalar fields for Bayer Non-Linear Mean denoise. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

The LUT helper asserts monotonic thresholds and 2..16 entry counts. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 188 lines, 6155 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm.host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm.host.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm.host.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm.host.h` is BNLM host declarations for the AtomISP CSS kernel host layer. declares VMEM encode, DMEM encode, and debug trace.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct bnlm_vmem_params *to,`, `struct bnlm_dmem_params *to,`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_BNLM_HOST_H`.

declares VMEM encode, DMEM encode, and debug trace. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

Generated parameter code for BNLM includes these helpers when that kernel is present. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 32 lines, 673 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm.host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm_param.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm_param.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm_param.h` is BNLM ISP parameter layouts for the AtomISP CSS kernel host layer. defines VMEM LUT/array layouts and DMEM scalar denoise parameters.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct bnlm_lut`, `struct bnlm_vmem_params`, `struct bnlm_lut mu_root_lut;`, `struct bnlm_lut sad_norm_lut;`, `struct bnlm_lut sig_detail_lut;`, `struct bnlm_lut sig_rad_lut;`, `struct bnlm_lut rad_pow_lut;`, `struct bnlm_lut nl_0_lut;`, `struct bnlm_lut nl_1_lut;`, `struct bnlm_lut nl_2_lut;`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_BNLM_PARAM_H`.

defines VMEM LUT/array layouts and DMEM scalar denoise parameters. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

The VMEM arrays depend on `ISP_VEC_NELEMS` and vector element width. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 56 lines, 1387 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm_param.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm_types.h -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm_types.h` is BNLM public config type for the AtomISP CSS kernel host layer. defines `struct ia_css_bnlm_config` with radial controls, exponential approximation coefficients, detail thresholds, match indexes, and many 15/16-entry LUTs.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_bnlm_config`. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_BNLM_TYPES_H`.

defines `struct ia_css_bnlm_config` with radial controls, exponential approximation coefficients, detail thresholds, match indexes, and many 15/16-entry LUTs. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

Host encoding copies these public tuning tables into firmware-vector layout. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 98 lines, 2529 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnlm/ia_css_bnlm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2.host.c -->
# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2.host.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2.host.c` is BNR2.2 host encoder for the AtomISP CSS kernel host layer. defines default BNR2.2 tuning, copies all public gain/threshold/detail fields into DMEM, and traces each field when debug is enabled.

## Important APIs, Types, and Functions

Visible functions: `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`, `ia_css_debug_dtrace`. Visible structs: `struct sh_css_isp_bnr2_2_params *to,`. Visible enums: none visible in this file. Important macros/constants: none visible in this file.

defines default BNR2.2 tuning, copies all public gain/threshold/detail fields into DMEM, and traces each field when debug is enabled. The file is part of the kernel-specific parameter path used by generated CSS parameter processing.

## Control Flow

It ignores `size`, so correctness depends on generated offsets selecting the right parameter block. In the broader pipeline, public CSS config is cached in `struct ia_css_isp_parameters`, generated parameter dispatch notices a nonzero memory offset for this kernel, and this host helper converts that public representation into the ISP-facing DMEM, VMEM, VAMEM, or HMEM layout.

## State and Persistence Behavior

This file owns no file-backed persistence. Defaults are compile-time constants when present; encoded state is written into per-binary parameter memory and remains there until the binary/stage is updated, reloaded, or freed.

## Dependencies and Integration Points

It depends on shared AtomISP CSS types, vector or memory-layout helpers when needed, and generated parameter dispatch from `ia_css_isp_params.c`. Firmware integration is by byte/layout compatibility of the target parameter structs.

## Risks and Edge Cases

Risk centers on size/layout drift, ignored `size` arguments, vector-width assumptions, and public tuning ranges that are only asserted in debug builds. Encoder changes must be checked against firmware binaries and generated memory offsets.

## Test Signals

Build the AtomISP driver with this kernel enabled, exercise default config and an explicit non-default config through `ia_css_pipe_set_isp_config()` or stream config paths, and verify generated dirty flags cause the expected memory class upload. Source read size: 123 lines, 3937 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/isp/kernels/bnr/bnr2_2/ia_css_bnr2_2.host.c -->
