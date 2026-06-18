# subset-b-001466 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/vmid/vmid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/vmid/vmid.c

## Purpose
This file implements the Display Core `mod_vmid` helper that maps display page table base addresses to hardware VMID slots. It is a small stateful allocator around `dc_setup_vm_context()`: physical addressing uses VMID 0, while nonzero page table bases are cached in VMIDs 1..`num_vmid - 1`.

## Important APIs, Types, And Functions
`struct core_vmid` embeds public `struct mod_vmid`, owns the `struct dc *` integration handle, tracks `num_vmid`, `num_vmids_available`, the `ptb_assigned_to_vmid[MAX_VMID]` table, and a base `dc_virtual_addr_space_config` copied at creation.

`mod_vmid_create()` validates that more than one VMID exists and that `dc` is non-null, allocates with `kzalloc_obj()`, stores the base VA config, initializes the free count to `num_vmid - 1`, and returns the embedded public object. `mod_vmid_destroy()` frees the containing `core_vmid`.

`mod_vmid_get_for_ptb()` is the exported lookup/allocate path. It returns VMID 0 for `ptb == 0`, reuses an existing mapping when present, evicts stale table entries if no VMID is available, chooses the next empty VMID, records the PTB, and programs Display Core by calling `dc_setup_vm_context(core_vmid->dc, &va_config, vmid)`.

Internal helpers are `add_ptb_to_table()`, `clear_entry_from_vmid_table()`, `evict_vmids()`, `get_existing_vmid_for_ptb()`, and `get_next_available_vmid()`.

## Control Flow
The allocator first treats zero PTB as physical addressing and short-circuits to VMID 0. For nonzero PTBs it performs a linear search across the tracked table. On a miss, it clones `base_config`, sets `page_table_base_addr`, and checks `num_vmids_available`. If the count is zero, `evict_vmids()` asks DC for the current use vector via `dc_get_vmid_use_vector()` and clears table entries for VMIDs whose bit is no longer active. After that, `get_next_available_vmid()` scans from VMID 1 upward. A successful allocation decrements the free count, stores the PTB, and programs the hardware VM context.

`mod_vmid_reset()` clears all cached PTB mappings and resets the free count to `num_vmid - 1`. There is no attempt to reprogram hardware during reset; the table is only the module's software cache.

## State And Persistence
All state is in the heap-allocated `core_vmid` object. It is runtime-only and persists until `mod_vmid_destroy()` or `mod_vmid_reset()`. `ptb_assigned_to_vmid[]` is the authoritative local cache; hardware state is indirectly synchronized when new mappings call `dc_setup_vm_context()`. VMID 0 is reserved and never allocated for PTBs.

## Dependencies And Integration Points
The file includes `mod_vmid.h`, which is provided under `display/modules/inc`. It depends on Display Core APIs and types: `struct dc`, `struct dc_virtual_addr_space_config`, `dc_setup_vm_context()`, and `dc_get_vmid_use_vector()`. It also uses kernel/display infrastructure such as `container_of`, `ASSERT`, `kzalloc_obj`, `kfree`, `memset`, `uint64_t`, and `uint8_t`.

The important downstream integration is with DCN VM context programming. This module decides which VMID to request, while lower display hardware code owns the actual register programming and the VMID use vector.

## Risks
The implementation assumes single-threaded or externally serialized access. There is no lock around `ptb_assigned_to_vmid[]` or `num_vmids_available`, so concurrent callers could double-allocate or corrupt the free count.

`add_ptb_to_table()` and `clear_entry_from_vmid_table()` only check `vmid < MAX_VMID`, not `vmid < num_vmid`; callers currently satisfy that by scanning to `num_vmid`, but future direct callers could create inconsistent state. The free counter can also drift if a table entry is cleared twice or added over an occupied VMID.

`evict_vmids()` casts the use vector to `uint16_t` after asserting it is at most `0xFFFF`, so hardware exposing more than 16 meaningful VMIDs would need a broader representation. A post-eviction allocation failure only asserts and still returns the current `vmid` value after the assert path, so production behavior depends on how `ASSERT` is compiled.

## Test Signals
Useful tests are allocation reuse for the same PTB, VMID 0 for PTB 0, allocation order from VMID 1 upward, reset clearing all mappings, and eviction behavior when `dc_get_vmid_use_vector()` marks entries unused. Integration tests should verify `dc_setup_vm_context()` receives a copied base config with only `page_table_base_addr` changed and that display workloads with VM context churn do not hit the assertion path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/vmid/vmid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/aldebaran_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/aldebaran_ip_offset.h

## Purpose
This generated-style header provides Aldebaran ASIC register base offsets by hardware IP block, instance, and segment. It is consumed during ASIC bring-up to populate `adev->reg_offset[hwip][instance]` so common register access macros can add block-specific base addresses.

## Important APIs, Types, And Data
The header defines `MAX_INSTANCE` as 7 and `MAX_SEGMENT` as 6, then declares `struct IP_BASE_INSTANCE { unsigned int segment[MAX_SEGMENT]; }` and `struct IP_BASE { struct IP_BASE_INSTANCE instance[MAX_INSTANCE]; }`.

It exports static constant `IP_BASE` tables for Aldebaran IP blocks including `ATHUB_BASE`, `CLK_BASE`, `DBGU_IO0_BASE`, `DF_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `IOAGR0_BASE`, `IOAPIC0_BASE`, `IOHC0_BASE`, `L1IMUIOAGR0_BASE`, `L1IMUPCIE0_BASE`, `L2IMU0_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIO_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SDMA0_BASE` through `SDMA4_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `VCN_BASE`, `WAFL0_BASE`, `WAFL1_BASE`, and `XGMI0_BASE` through `XGMI2_BASE`.

For each table, it also emits flattened macros such as `ATHUB_BASE__INST0_SEG0`, `NBIO_BASE__INST0_SEG5`, or `XGMI2_BASE__INST5_SEG1`. These are compile-time constants for code that wants preprocessor-level offsets instead of walking the table.

## Control Flow
There are no functions. Control flow happens in the including ASIC initialization file. `aldebaran_reg_base_init()` includes this header and loops over `i < MAX_INSTANCE`, assigning selected table instances into `adev->reg_offset` for `GC`, `HDP`, `MMHUB`, `ATHUB`, `NBIO`, `MP0`, `MP1`, `DF`, `OSSSYS`, `SDMA0` through `SDMA4`, `SMUIO`, `THM`, `UMC`, and `VCN`.

## State And Persistence
The header contributes immutable static data compiled into the driver. Runtime state is created when the driver stores pointers to table instances in `adev->reg_offset`. The data itself is not persisted beyond the loaded kernel module image and is not modified.

## Dependencies And Integration Points
The table shape must match `adev->reg_offset` expectations in the AMDGPU SOC15 register access layer. It is tightly coupled to `amdgpu/aldebaran_reg_init.c`, SOC15 hardware IP identifiers, and all register headers whose `mm*` offsets are resolved relative to these base segments.

## Risks
Because this is address-map data, a single wrong offset can make register reads or writes hit the wrong block. Many instances and segments are zero placeholders; caller code must distinguish absent mappings from valid segment 0 values where appropriate. The generic `struct IP_BASE` name is shared by other ASIC offset headers, so multiple such headers should not be included in the same compilation unit unless guarded by local conventions.

`MAX_INSTANCE` and `MAX_SEGMENT` are part of the ABI with initialization loops and register-offset consumers. Changing either without updating the associated ASIC init path can leave offsets uninitialized or cause out-of-bounds assumptions.

## Test Signals
Compile coverage of `aldebaran_reg_base_init()` catches structural breakage. Hardware or emulation smoke tests should read known stable registers for every initialized HWIP and verify nonzero base segments match the ASIC address map. RAS, SDMA, VCN, MMHUB, ATHUB, and UMC initialization are strong integration signals because they exercise different populated base tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/aldebaran_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_acpi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_acpi.h

## Purpose
This header defines AMD GPU ACPI method data contracts and constants for ATIF, ATPX, ATRM, and ATCS firmware interfaces. It is a shared ABI header between AMDGPU ACPI handling code and platform firmware buffers.

## Important APIs, Types, And Constants
Packed structures model method input and output buffers: `atif_verify_interface`, `atif_system_params`, `atif_sbios_requests`, `atif_qbtc_arguments`, `atif_qbtc_data_point`, `atif_qbtc_output`, `atcs_verify_interface`, `atcs_pref_req_input`, `atcs_pref_req_output`, `atcs_pwr_shift_input`, `atcs_get_uma_size_output`, and `atcs_set_uma_allocation_size_input`.

ATIF constants define function IDs and bit flags for interface verification, system parameters, system BIOS requests, thermal notifications, brightness transfer characteristics, undock notification, and external GPU information. ATPX constants define PowerXpress interface verification, PX parameters, dGPU power control, display and I2C mux control, switch notifications, connector mapping, and detection ports. ATCS constants define chipset-specific external state, PCIe performance requests, device-ready notification, bus-width control, power-shift control, UMA size query, and UMA allocation sizing.

`ATIF_QBTC_MAX_DATA_POINTS` is 99. The file has static assertions tying `atif_qbtc_data_point` to `amdgpu_dm_luminance_data` and the max point count to `MAX_LUMINANCE_DATA_POINTS`, so display-manager brightness-curve parsing depends on this layout.

## Control Flow
There is no executable code. Runtime control flow is driven by callers such as `amdgpu_acpi.c`, `amdgpu_atpx_handler.c`, and PowerPlay hardware-manager code. Those callers check the `*_SUPPORTED` function bitmasks, construct the packed input buffers, invoke ACPI control methods, then parse output buffers according to these structures and flags.

## State And Persistence
This header defines firmware ABI state but stores none itself. The values are transient ACPI method buffers and notification flags. Some data, such as supported function bits, pending SBIOS requests, connector mappings, external GPU info, power source, and brightness curves, may be cached by callers after parsing.

## Dependencies And Integration Points
The header includes `<linux/types.h>` and relies on packed layout compatibility with ACPI firmware. It integrates with display brightness handling, PowerXpress dGPU power and mux switching, PCIe performance requests, dock/external-state handling, UMA sizing, and system BIOS notifications.

The ATIF, ATPX, ATRM, and ATCS method comments in the file are part of the integration contract: each method receives an integer function code plus a 256-byte parameter buffer except ATRM, which fetches VBIOS ROM data by offset and size.

## Risks
The main risk is ABI drift. Structure padding, field width, or packed layout mistakes can misparse firmware buffers. Firmware may report unsupported functions, shorter structures, invalid sizes, or inconsistent masks, so callers must validate `size`, support bits, and error codes before consuming fields.

Brightness-curve structures are tied to display-manager constants through static assertions. If either side changes, this header deliberately breaks compilation rather than allowing incompatible luminance data parsing.

## Test Signals
Compile tests should cover all include sites and the static assertions. Runtime signals include ACPI method discovery on hybrid graphics systems, dGPU power switching, mux switching, external GPU enumeration, AC/DC power-source notifications, panel brightness notifications, custom brightness curve parsing, PCIe performance requests, and UMA sizing on APUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_acpi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_cper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_cper.h

## Purpose
This header defines AMDGPU Common Platform Error Record structures, GUIDs, revisions, severities, and register-dump layouts used for GPU RAS crash, boot, and nonstandard error reporting.

## Important APIs, Types, And Constants
Constants include `CPER_HDR_REV_1`, section revision values, `CPER_MAX_OAM_COUNT`, context types `CPER_CTX_TYPE_CRASH` and `CPER_CTX_TYPE_BOOT`, and `CPER_CREATOR_ID_AMDGPU`. GUID macros identify notification types (`CPER_NOTIFY_MCE`, `CPER_NOTIFY_CMC`, `BOOT_TYPE`) and section types (`AMD_CRASHDUMP`, `AMD_GPU_NONSTANDARD_ERROR`, `PROC_ERR_SECTION_TYPE`).

`enum cper_error_severity` represents corrected, nonfatal uncorrected, fatal, and unused severities. `enum cper_aca_reg` names the low/high ACA register slots with `CPER_ACA_REG_COUNT` set to 32.

Packed structures define the binary record format: `cper_timestamp`, `cper_hdr`, `cper_sec_desc`, `cper_sec_nonstd_err_hdr`, `cper_sec_nonstd_err_info`, `cper_sec_nonstd_err_ctx`, `cper_sec_nonstd_err`, `cper_sec_crashdump_hdr`, `cper_sec_crashdump_reg_data`, `cper_sec_crashdump_body_fatal`, `cper_sec_crashdump_body_boot`, `cper_sec_crashdump_fatal`, and `cper_sec_crashdump_boot`.

## Control Flow
There are no functions. RAS and CPER producer/consumer code includes this header, fills a `cper_hdr`, appends section descriptors, and serializes one of the section bodies depending on whether the event is runtime nonstandard error, fatal crashdump, or boot/OAM message data.

## State And Persistence
The structures describe persisted firmware/OS error records. The header itself has no mutable state, but the records it formats may be stored in RAS buffers, exposed via debugfs/sysfs or command paths, and retained as platform error evidence.

## Dependencies And Integration Points
The only direct include is `<linux/uuid.h>` for `guid_t` and `GUID_INIT`. In this source tree, `amdgpu/amdgpu_cper.h` includes this file, and RAS command paths reference CPER snapshot and record retrieval. The data layout must also align with platform CPER consumers outside AMDGPU.

## Risks
The header uses `#pragma pack(push, 1)` around the binary layouts. Any accidental field change affects externally consumed record offsets. Bitfields inside fixed-width integers are convenient for driver code but should be treated cautiously across compiler and endian assumptions; serialization tests should inspect masks, not just named bitfields.

There is a nearby RAS-specific CPER header in `ras/rascore/ras_cper.h` with similar concepts and different names/counts. Keeping both definitions coherent is important to avoid converting or interpreting records with the wrong layout.

## Test Signals
Compile coverage through `amdgpu_cper.h` is the first signal. Stronger validation should build representative fatal, boot, and nonstandard records and assert exact sizes, offsets, GUID bytes, section lengths, and severity values. RAS command tests for CPER snapshot and CPER record retrieval are integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_cper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_pcie.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_pcie.h

## Purpose
This header centralizes AMDGPU PCIe link speed and lane-width capability bitmasks. It encodes both platform/chipset support and ASIC hardware support in one 32-bit capability value.

## Important APIs, Types, And Constants
Speed capability masks use low bits for ASIC support (`CAIL_ASIC_PCIE_LINK_SPEED_SUPPORT_GEN1` through `GEN5`, mask `0x0000FFFF`, shift 0) and high bits for driver/platform support (`CAIL_PCIE_LINK_SPEED_SUPPORT_GEN1` through `GEN5`, mask `0xFFFF0000`, shift 16).

Lane-width masks follow the same split: ASIC support uses low bits for x1, x2, x4, x8, x12, x16, and x32; platform/driver support uses the corresponding high bits. Defaults are `AMDGPU_DEFAULT_PCIE_GEN_MASK`, `AMDGPU_DEFAULT_PCIE_MLW_MASK`, and `AMDGPU_DEFAULT_ASIC_PCIE_MLW_MASK`.

## Control Flow
The header has no executable logic. Callers include it to compose default masks, filter VBIOS/firmware/platform capabilities, and pass capability values into helpers or power-management code.

## State And Persistence
No state is stored in this header. The masks are compile-time constants. Runtime state lives in AMDGPU device and power-management structures that store supported PCIe generations and lane widths.

## Dependencies And Integration Points
It is included by many AMDGPU SOC, KMS, device, DPM, SMU, KFD, and legacy power-management files. `amd_pcie_helpers.h` depends directly on these masks to choose requested PCIe generation and lane width. ACPI ATCS PCIe requests in `amd_acpi.h` are a related platform-control interface.

## Risks
The split low/high encoding must stay consistent across all callers. Confusing ASIC bits with platform bits can make the driver request an unsupported generation or lane width. The default generation mask includes platform Gen1/Gen2 and ASIC Gen1/Gen2/Gen3 but not newer Gen4/Gen5, so newer hardware paths need explicit capability population rather than relying only on defaults.

## Test Signals
Compile coverage through all include sites catches macro renames. Unit-style tests around capability construction should verify the low/high masks and shifts. Runtime test signals include DPM-reported PCIe capabilities, link retraining, forced performance levels, suspend/resume link restoration, and KFD interop on systems with different lane widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_pcie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_pcie_helpers.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_pcie_helpers.h

## Purpose
This header provides inline helpers that convert AMDGPU PCIe capability bitmasks into selected PCIe generation and lane-width values for PowerPlay hardware managers.

## Important APIs, Types, And Functions
`is_pcie_gen3_supported()` and `is_pcie_gen2_supported()` test the high platform support bits from `amd_pcie.h`.

`get_pcie_gen_support(uint32_t pcie_link_speed_cap, uint16_t ns_pcie_gen)` returns a `PP_PCIEGen*` value. It first extracts ASIC speed support bits. If the ASIC mask is exactly Gen1, Gen2, or Gen3, it returns that generation. Otherwise it uses system support bits and the requested new-state generation to choose Gen3, fall back to Gen2, or default to Gen1.

`get_pcie_lane_support(uint32_t pcie_lane_width_cap, uint16_t ns_pcie_lanes)` returns the closest supported lane count. Exact single-bit masks map directly to x1, x2, x4, x8, x12, x16, or x32. For multi-bit masks, it searches the standard lane array, keeps the requested width if supported, otherwise searches downward first and upward second.

## Control Flow
Both selection helpers are straight-line decision logic with switch statements and fallback scans. Generation selection prefers exact ASIC-only declarations before considering system capability plus the requested performance state. Lane selection prefers exact single-width declarations, then nearest lower supported width, then nearest higher supported width.

## State And Persistence
The helpers are stateless inline functions. They read passed-in capability masks and return selected values; callers persist the result in power-management state if needed.

## Dependencies And Integration Points
The header includes `amd_pcie.h` and uses `PP_PCIEGen1`, `PP_PCIEGen2`, and `PP_PCIEGen3` from the PowerPlay hardware-manager API. It is included by SMU7, Vega10, Vega12, and Vega20 hardware manager code. It also uses `pr_err()` for invalid lane capability diagnostics, relying on kernel logging availability through include context.

## Risks
`get_pcie_gen_support()` compares the extracted ASIC mask for exact equality to single-generation values. If firmware reports multiple ASIC generation bits, the code falls into the system-capability path instead of selecting the highest ASIC-supported generation directly.

`get_pcie_lane_support()` only understands the seven lane values in its local array. Unsupported requested values are returned unchanged unless they match one of those array entries. The final `if (j > 7)` check is unreachable for a failed upward search ending at `j == 7`, so the intended error log for no valid upward lane width is not emitted.

## Test Signals
Focused tests should cover exact Gen1/Gen2/Gen3 ASIC masks, multi-bit speed masks, requested Gen3 falling back to Gen2, zero lane masks, exact single lane masks, multi-lane masks with requested width supported, fallback to lower width, fallback to higher width, and invalid requested lane counts. Runtime signals are correct DPM tables and stable PCIe link behavior when forcing power/performance states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_pcie_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_shared.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_shared.h

## Purpose
This header defines shared AMDGPU concepts used across display, KFD, PowerPlay, SMU, and core device code: chip flags, APU flags, IP block types, clock/power gating states, feature masks, debug masks, and the common `amd_ip_funcs` lifecycle callback table.

## Important APIs, Types, And Constants
Chip flags distinguish ASIC identity bits from driver flags such as mobility, APU, PX, and experimental support. APU flags enumerate Raven, Raven2, Picasso, Renoir, Green Sardine, Vangogh, and Cyan Skillfish2.

`enum amd_ip_block_type` classifies GPU IP blocks: common, GMC, IH, SMC, PSP, DCE, GFX, SDMA, UVD, VCE, ACP, VCN, MES, JPEG, VPE, UMSCH_MM, ISP, RAS, and count. `enum amd_clockgating_state` and `enum amd_powergating_state` define gate/ungate control values.

Clock-gating and power-gating support macros define bit flags for GFX, memory controller, SDMA, BIF, UVD, VCE, HDP, ROM, DRM, DF, VCN, ATHUB, JPEG, repeater, IH, and other blocks. `enum PP_FEATURE_MASK` defines boot-tunable PowerPlay feature bits. `enum DC_FEATURE_MASK` and `enum DC_DEBUG_MASK` define display feature and debug toggles.

`struct amd_ip_funcs` is the central lifecycle interface for IP blocks. It contains callbacks for early/late/software/hardware init and fini, suspend/resume, idle checks, soft reset phases, clock/power gating, clock-gating state dump, IP state dump, and devcoredump printing.

## Control Flow
There is no executable code, but `struct amd_ip_funcs` drives AMDGPU device lifecycle control. The core driver builds an ordered list of IP blocks, then calls the appropriate callbacks during probe, init, suspend, resume, reset, power management, and diagnostic dump paths.

## State And Persistence
The header stores no runtime state. It defines enum and mask values that are persisted in device structures, module parameters, DPM state, display debug configuration, and per-IP block descriptors. Feature masks can be influenced by boot/module parameters such as `amdgpu.ppfeaturemask`.

## Dependencies And Integration Points
It includes `<drm/amd_asic_type.h>` and `<drm/drm_print.h>`, forward-declares `struct amdgpu_ip_block`, and references `struct drm_printer`. It is included by AMDGPU core headers, KFD private headers, display manager code, PowerPlay, and CGS common interfaces.

The `amd_ip_funcs` callback table is implemented by many IP-specific files, including GFX, SDMA, JPEG, VCN, VPE, DCE, SMU, and legacy DPM implementations. Power-management code uses `AMD_IP_BLOCK_TYPE_*` values to request gating by block.

## Risks
Enum ordering is semantically important where arrays are sized by `AMD_IP_BLOCK_TYPE_NUM` or indexed by block type. Adding, removing, or reordering values can break existing state arrays unless all users are updated.

Feature/debug mask bits are externally visible through module parameters and diagnostics. Reusing a bit or changing its meaning can silently alter user configuration. Callback pointers in `amd_ip_funcs` are optional in practice, so core callers must check availability or ensure a callback is mandatory for that lifecycle phase.

## Test Signals
Build coverage across AMDGPU is required because this header is broad. Runtime signals include successful IP block init/fini ordering, suspend/resume, GPU reset, clock-gating and power-gating toggles, devcoredump generation, and module-parameter feature-mask behavior. Tests that inspect `AMD_IP_BLOCK_TYPE_NUM`-sized arrays are important after enum changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amd_shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amdgpu_reg_state.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amdgpu_reg_state.h

## Purpose
This header defines the binary/sysfs format used to expose selected AMDGPU register state snapshots for XGMI, WAFL, PCIe, and user-defined state groups.

## Important APIs, Types, And Constants
`enum amdgpu_reg_state` defines state types: invalid, XGMI, WAFL, PCIe, USR, and USR_1. `enum amdgpu_sysfs_reg_offset` assigns sysfs read offsets in 0x1000-sized windows from XGMI through USR_1, ending at `0x5000`.

`struct amdgpu_reg_state_header` is the common file/record header with structure size, format revision, content revision, state type, number of instances, and padding. `enum amdgpu_reg_inst_state` reports per-instance status: OK, disabled, or access error.

`struct amdgpu_smn_reg_data` stores an SMN address/value pair. `struct amdgpu_reg_inst_header` stores instance number, state, and register count. Flexible-array structures model XGMI, WAFL, PCIe, and user state payloads. PCIe instances additionally store PCI config/status fields such as device status, link status, sub-bus/latency, and correctable/uncorrectable error statuses.

`amdgpu_reginst_size()` computes the combined size for repeated instance records. Macros `amdgpu_asic_get_reg_state_supported()` and `amdgpu_asic_get_reg_state()` dispatch through `adev->asic_funcs->get_reg_state`. `amdgpu_reg_state_sysfs_init()` and `amdgpu_reg_state_sysfs_fini()` declare sysfs lifecycle hooks.

## Control Flow
The header does not implement sysfs reads, but it defines the flow: sysfs init registers a binary attribute, users read an offset range corresponding to a state type, the implementation calls the ASIC `get_reg_state` hook if present, and the hook fills a buffer using the header and flexible-array layouts.

## State And Persistence
The structures represent transient snapshots of hardware and SMN state. They are exposed through sysfs offsets but are not persistent storage. The only durable contract is the binary layout and offset partitioning, which user-space tools may depend on.

## Dependencies And Integration Points
The header is included by `amdgpu.h`, `soc15.h`, and ASIC-specific code such as `aqua_vanjaram.c`. It depends on `struct amdgpu_device` and `adev->asic_funcs->get_reg_state` being defined by broader AMDGPU headers. It integrates with sysfs and hardware-specific register dump providers.

## Risks
Flexible arrays require careful size calculation and bounds checking. A mismatch between `num_instances`, `num_smn_regs`, and buffer length can corrupt output or truncate records. The sysfs offset constants are a user-visible ABI; changing them can break tools that read specific windows.

The dispatch macro returns 0 if no hook exists, which can be ambiguous if callers treat 0 as success with zero bytes. Callers should separately check support with `amdgpu_asic_get_reg_state_supported()`.

## Test Signals
Tests should validate exact structure sizes, `amdgpu_reginst_size()` arithmetic, sysfs offset routing, unsupported-ASIC behavior, and buffer-bound handling. Integration signals include successful sysfs reads for XGMI/WAFL/PCIe/user snapshots and correct disabled/access-error reporting per instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/amdgpu_reg_state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/arct_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/arct_ip_offset.h

## Purpose
This generated-style header provides Arcturus ASIC register base offsets by hardware IP block, instance, and segment. It feeds the SOC15 register-offset table so shared AMDGPU register macros resolve to the correct Arcturus base addresses.

## Important APIs, Types, And Data
The header defines `MAX_INSTANCE` as 8 and `MAX_SEGMENT` as 6. It declares `struct IP_BASE_INSTANCE` and `struct IP_BASE` with `__maybe_unused` annotations.

Static `IP_BASE` tables cover `ATHUB_BASE`, `CLK_BASE`, `DF_BASE`, `FUSE_BASE`, `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, `MP0_BASE`, `MP1_BASE`, `NBIF0_BASE`, `OSSSYS_BASE`, `PCIE0_BASE`, `SDMA0_BASE` through `SDMA7_BASE`, `SMUIO_BASE`, `THM_BASE`, `UMC_BASE`, `UVD_BASE`, `DBGU_IO_BASE`, and `RSMU_BASE`. Flattened `*_BASE__INSTn_SEGm` macros mirror the tables for compile-time use.

Arcturus has eight instance slots. Several tables use all or many slots, notably UMC and SDMA, while many control IPs only populate instance 0 and leave remaining slots as zero.

## Control Flow
There are no functions. `arct_reg_base_init()` includes this header and loops over `i < MAX_INSTANCE`, storing table instance pointers into `adev->reg_offset` for `GC`, `HDP`, `MMHUB`, `ATHUB`, `NBIO` from `NBIF0_BASE`, `MP0`, `MP1`, `UVD`, `DF`, `OSSSYS`, `SDMA0` through `SDMA7`, `SMUIO`, `THM`, `UMC`, and `RSMU`.

## State And Persistence
The header provides immutable compiled-in data. Runtime state is the `adev->reg_offset` pointer table populated from it during device initialization. No offsets are modified or persisted by this header.

## Dependencies And Integration Points
The data shape is coupled to AMDGPU SOC15 register infrastructure and `amdgpu/arct_reg_init.c`. It supports register access for graphics, memory hub, ATHUB, NBIF/PCIe, SDMA engines, UVD, thermal, SMU, UMC, and RSMU blocks on Arcturus.

## Risks
Wrong base addresses can cause register operations to target incorrect hardware blocks. Because this header defines generic `IP_BASE` type names also used by other ASIC offset headers, it should remain isolated to one ASIC init compilation unit.

The Arcturus init code maps `NBIO_HWIP` to `NBIF0_BASE`, so naming changes in this header need coordinated updates. `MAX_INSTANCE` is 8 here, unlike Aldebaran's 7; common code must not assume all SOC15 ASIC offset headers use the same instance count.

## Test Signals
Build coverage of `arct_reg_base_init()` catches symbol and type breakage. Runtime validation should include register reads for every initialized HWIP, especially all SDMA instances, UMC instances, ATHUB, NBIF/PCIe, and RSMU. Comparing populated `adev->reg_offset` entries against known Arcturus address-map data is the key regression test.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/arct_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_0_offset.h

## Purpose
This generated register-offset header defines ATHUB 1.0 register offsets and base-index selectors. ATHUB handles address translation services, VMID-to-PASID mapping, PCIe ATS/PASID/page-request controls, crossbar/routing, peer-to-peer BAR mappings, queues, arbitration, and performance counters.

## Important APIs, Types, And Constants
The file has no types or functions; it is a list of `mm*` register offset macros paired with `*_BASE_IDX` macros. All base indices in this header are 0.

Registers are grouped into three address blocks:

`athub_atsdec` at base address `0x3080` defines `mmATC_ATS_CNTL`, status and fault registers, default page controls, VMID/PASID mapping update status, `mmATC_VMID0_PASID_MAPPING` through `mmATC_VMID31_PASID_MAPPING`, ATS VMID and ATCL2 status, ATC performance counters, PCIe ATS/PASID/page-request controls, per-VF ATS controls, memory power, IH credits, shared virtualization reset/active function registers, and VMID snapshot status registers.

`athub_xpbdec` at base address `0x31f0` defines XPB router source apertures, XDMA router apertures, destination maps, CLG config/match/unit-ID mappings, local/host/interface status, P2P BAR registers, peer system BAR registers, clock gating, pipe/sub-control, sticky status, and performance knobs.

`athub_rpbdec` at base address `0x33b0` defines RPB pass/block/tag configuration, efficiency and arbitration controls, BIF controls, read/write switch controls, CID and EA queue registers, virtual-channel switch, performance counters, queue controls, ATS controls, and SDP port control.

## Control Flow
There is no executable control flow. Including code combines these offsets with the ATHUB base segment in the ASIC-specific IP offset table, then reads or writes the resulting addresses through AMDGPU register access macros.

## State And Persistence
This header stores no state. The macros name hardware registers that contain live GPU state such as mappings, faults, counters, queue settings, and virtualization controls. Persistence is entirely in hardware until reset or reprogramming by the driver.

## Dependencies And Integration Points
The header is included by ATHUB and memory-management code such as `athub_v1_0.c`, `gmc_v9_0.c`, `mmhub_v9_4.c`, and KFD GFX v9 integration code. It depends on ASIC offset headers, such as Aldebaran or Arcturus IP base tables, to supply the block base address for base index 0.

It integrates with VMID/PASID setup, ATS fault handling, PCIe ATS enablement, SR-IOV per-VF controls, interrupt credit handling, peer-to-peer routing, clock-gating setup, and performance-counter paths.

## Risks
Generated register offsets are low-level hardware ABI. An incorrect offset can break address translation, VMID/PASID isolation, fault reporting, virtualization reset, or peer routing. Because this header provides offsets only, callers must use the matching mask/shift header when manipulating fields; hard-coded bit operations around these offsets are riskier.

The VMID mapping range extends through VMID31, while other display-side VMID code may use smaller VMID counts. Callers must respect the IP block's supported VMID range and the ASIC's configured VMID policy.

## Test Signals
Compile coverage through all include sites catches missing symbols. Runtime signals include successful ATHUB initialization, ATS enable/disable, PASID mappings for VMIDs 0-31 as applicable, recoverable fault reporting, SR-IOV VF ATS programming, KFD queue operation, peer-to-peer BAR routing, ATHUB clock-gating transitions, and performance-counter reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_1_0_offset.h -->
