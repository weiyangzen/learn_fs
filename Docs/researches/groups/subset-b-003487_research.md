# Research: subset-b-003487

Grouped research for AMDGPU firmware ABI, generated IP-base, CGS, and CIK queue context headers. Each section preserves the exact source path in its title and is bounded for reconciliation into source-tree-aligned per-file outputs.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmware.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmware.h

## Purpose

`atomfirmware.h` is the packed ABI contract between AMD ATOM VBIOS firmware, pre-OS firmware, tools, and Linux AMDGPU/PowerPlay/Display code for SoC15-and-newer devices. It does not implement algorithms; it defines the byte-exact table headers, table directories, data-table payloads, command-parameter payloads, ACPI VFCT payloads, scratch-register bit assignments, and enum constants that consumers use when parsing a GPU VBIOS image or invoking ATOM command tables.

The file is intentionally versioned by table structure names and embedded `atom_common_table_header` revisions. Consumers select a table by master-table offset, inspect `format_revision` and `content_revision`, then cast the firmware bytes to the matching `struct atom_*_vX_Y` layout. The global `#pragma pack(1)` is part of the ABI: every field offset must match the VBIOS binary layout.

## Important APIs, Types, and Macros

The header exports data layouts and constants only; there are no functions or mutable globals.

Major ABI foundations:

- `enum atom_bios_header_version_def`, `BIOS_ATOM_PREFIX`, `BIOS_VERSION_PREFIX`, `BIOS_STRING_LENGTH`, and `enum atombios_image_offset` define ROM identification and fixed offsets such as `OFFSET_TO_ATOM_ROM_HEADER_POINTER`.
- `struct atom_common_table_header` prefixes all command/data tables with `structuresize`, `format_revision`, and `content_revision`.
- `struct atom_rom_header_v2_2` locates the command and data master tables through `masterhwfunction_offset` and `masterdatatable_offset`.
- `struct atom_master_list_of_command_functions_v2_1` and `struct atom_master_command_function_v2_1` publish command offsets for ASIC init, clocks, CRTC/display operations, I2C/AUX transactions, voltage, memory training, and encoder/transmitter controls.
- `struct atom_master_list_of_data_tables_v2_1` and `struct atom_master_data_table_v2_1` publish data table offsets for firmware info, LCD info, GPIO LUT, display object info, DCE/DCN info, integrated system info, graphics, SMU, SMC DPM, UMC, VRAM, voltage objects, profiling, and powerplay data.

Important data-table families:

- Firmware info: `atom_firmware_info_v3_1` through `v3_5`, plus `enum atombios_firmware_capability`, carry boot clocks, boot voltages, memory controller base, firmware-reserved FB size, PSP bootloader polling data, SPI ROM size, display PHY tuning size, and feature flags.
- Display and panel metadata: `atom_dtd_format`, `lcd_info_v2_1`, GPIO pin LUT structures, display object records, display path structures, connector capability records, bracket layout records, and external display path records describe connectors, HPD/AUX/DDC, board retimers/redrivers, panel power sequencing, and supported device tags.
- DC/DCE/DCN info: `atom_display_controller_info_v4_1` through `v4_5`, `atom_dc_golden_table_v1`, and `enum dce_info_caps_def` describe display clock/reference data, spread spectrum, pipe/PHY/AUX counts, golden AUX/GPIO values, LTTPR flags, and memory-clock/self-refresh latency hints.
- Integrated system info: `atom_integrated_system_info_v1_11`, `v1_12`, `v2_1`, `v2_2`, `v2_3`, `edp_info_table`, camera structures, display PHY tuning sets, and UMA carveout options carry APU/platform display and memory-carveout configuration.
- GFX/SMU/SMC/UMC/VRAM: `atom_gfx_info_v2_2` through `v3_0`, `atom_smu_info_v3_1` through `v4_0`, `atom_smc_dpm_info_v4_1` through `v4_10`, `atom_umc_info_v3_1` through `v4_0`, `atom_vram_info_header_v2_3` through `v3_0`, and related module/timing/remap blocks define topology, boot clocks, spread spectrum, telemetry, I2C controllers, VR mapping, memory training, GDDR6 timings, and VRAM module data.
- Voltage objects: `atom_voltage_object_header_v4`, `atom_i2c_voltage_object_v4`, `atom_gpio_voltage_object_v4`, `atom_svid2_voltage_object_v4`, `atom_merged_voltage_object_v4`, `union atom_voltage_object_v4`, and `atom_voltage_objects_info_v4_1` describe board voltage control methods.

Important command-parameter families:

- ASIC, engine, memory, and voltage operations: `asic_init_*`, `set_engine_clock_*`, `set_memory_clock_*`, `get_engine_clock_parameter`, `get_memory_clock_parameter`, `set_voltage_*`, and associated flag enums.
- Clock computation and SMU clock discovery: `compute_gpu_clock_*`, `read_efuse_*`, `atom_get_smu_clock_info_*`, SMU9/11/12 SYSPLL IDs, and clock IDs.
- Memory/display commands: `dynamic_memory_settings_parameters_v2_1`, `memory_training_parameters_v2_1`, `set_pixel_clock_parameter_v1_7`, `set_dce_clock_parameters_v2_1`, CRTC blank/enable/power-gating structures, DTD timing, I2C/AUX transaction structures, CRTC source selection, DIG encoder, DIG transmitter, and external encoder control payloads.
- ACPI/scratch data: `amd_acpi_description_header`, `uefi_acpi_vfct`, `vfct_image_header`, GOP content blocks, and scratch-register enums for connect/active/request/backlight/pre-OS mode state.

The header ends by including `atomfirmwareid.h`, which binds compact data/command table IDs to this ABI.

## Control Flow

There is no control flow inside this header. Runtime flow is implemented by consumers that use these layouts:

- ATOM parser setup reads the ROM header pointer, casts the ROM header, follows `masterdatatable_offset` or `masterhwfunction_offset`, and then indexes one of the master lists to locate a target table/function.
- AMDGPU ATOM firmware helpers read a table header, branch on `format_revision` and `content_revision`, and cast to a matching versioned structure such as `atom_firmware_info_v3_1`, `v3_3`, `v3_4`, or `v3_5`.
- Power-management code loads SMC DPM info tables, copies version-specific board parameters into SMU powerplay tables, and uses firmware-info fields for boot frequencies, firmware reservations, PSP bootloader checks, and platform limits.
- Display code parses display object and integrated system info records to build connector, HPD, AUX/DDC, panel, retimer, eDP, and PHY-tuning state.
- Command-table callers fill one of the command parameter structures, invoke the ATOM BIOS parser for the relevant command-table offset, then read back output fields or status unions such as I2C/AUX transaction status.

## State and Persistence Behavior

The header has no runtime state of its own. It describes persistent and semi-persistent firmware-owned data:

- VBIOS image bytes persist in ROM or copied BIOS memory. These structures are views over that data, so every field is effectively persistent firmware configuration until a different VBIOS image is loaded.
- `vram_usagebyfirmware_v2_1` and `v2_2` describe reserved framebuffer regions. The comments specify driver behavior for posted and unposted VBIOS cases, pre-NV1X versus newer ASICs, and SR-IOV/PF-VF reservation exchange.
- Scratch-register definitions map firmware/driver communication bits for connected, active, requested, backlight, AC/lid, pre-OS mode, and ASIC-init state. Those bits live in hardware scratch registers, not in this header.
- Command parameter structures are transient call frames for ATOM parser invocations. Some commands cause durable hardware state changes: clock programming, memory training, voltage control, display power gating, encoder setup, I2C writes, and AUX transactions.

## Dependencies

The file depends on fixed-width integer types being available, except when `_H2INC` is used to provide simple typedefs for header-to-include conversion. It depends on kernel/compiler support for packed structures and includes `atomfirmwareid.h` at the end by design. Some flexible or variable-length payloads rely on C flexible arrays or kernel annotations such as `__counted_by`.

Consumers depend on AMDGPU infrastructure such as ATOM parser helpers, `amdgpu_atomfirmware.c`, `amdgpu_atomfirmware.h`, Display Core, PowerPlay/SMU code, VBIOS ROM access, and firmware-specific generated register headers. External correctness depends on VBIOS producer tools preserving these exact layouts and revisions.

## Integration Points

Direct and representative includes include:

- `drivers/gpu/drm/amd/amdgpu/atom.c`
- `drivers/gpu/drm/amd/amdgpu/amdgpu_atomfirmware.c`
- `drivers/gpu/drm/amd/display/dmub/inc/dmub_cmd.h`
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/*`
- `drivers/gpu/drm/amd/pm/swsmu/smu11/*`, `smu12/*`, `smu13/*`, `smu14/*`, and `smu15/*`

Representative call sites cast firmware bytes to `atom_firmware_info_v3_*`, `atom_smc_dpm_info_v4_*`, and display/VRAM/UMC tables. Beige Goby-specific SMU code uses `atom_smc_dpm_info_v4_9` fields to populate `PPTable_beige_goby_t`.

## Risks and Edge Cases

- This file is a binary ABI. Reordering, resizing, changing signedness, removing reserved fields, or dropping `#pragma pack(1)` breaks VBIOS parsing.
- Version handling is mandatory. A field present in `atom_firmware_info_v3_4` or `v3_5` cannot be read from `v3_1`; DPM and SMU table versions have similar incompatibilities.
- Many tables contain offsets to nested blocks or variable-length arrays. Consumers must bounds-check against `structuresize` and the containing BIOS image before casting or iterating.
- Several fields encode units in names or comments: 10 kHz, 100 Hz, 10 Hz, millivolts, milliwatts, KB, 16 MB chunks, Q formats, and 4 ms panel delays. Unit mistakes produce plausible but wrong hardware programming.
- The VRAM reservation rules are nuanced and differ by VBIOS posted state, generation, and SR-IOV role. Misinterpreting them can corrupt firmware-reserved framebuffer memory or hide a required PF/VF exchange area.
- Command structures use unions and in/out fields. Treating output status as valid before parser completion, or using the wrong command revision, can mask hardware failures.
- Some enum names preserve historical misspellings such as `EXTENAL`, `TUNNING`, and `THROTTLER/THROTTER`; renaming them can break existing source.

## Test Signals

- Compile coverage of AMDGPU, Display Core, PowerPlay, and SMU generations catches missing type/field names.
- VBIOS parsing tests should exercise table header revision dispatch, `structuresize` bounds, master data/command table offsets, and variable-length table walking.
- Boot tests across ASIC generations should validate firmware-info boot clocks, firmware-reserved memory, VRAM info, UMC training offsets, and SMU DPM board parameter ingestion.
- Display hotplug and mode-set tests validate display object records, HPD/AUX/DDC mapping, eDP panel power sequencing, spread-spectrum fields, retimer data, and DIG transmitter/encoder command payloads.
- Power-management tests should compare decoded SMC DPM telemetry, I2C controller settings, VR mapping, board power limits, spread spectrum, and boot clock fields against known-good VBIOS/SMU traces.
- SR-IOV tests should explicitly verify firmware/driver framebuffer reservation behavior and scratch/register communication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmware.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmwareid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmwareid.h

## Purpose

`atomfirmwareid.h` defines compact enum IDs for ATOM VBIOS master data tables and command tables. It is the ID companion to `atomfirmware.h`: `atomfirmware.h` defines the table directory layout and payload structures, while this file assigns stable symbolic IDs that helper code can use when asking for a specific VBIOS table or command by logical name.

## Important APIs, Types, and Macros

The header exports two enums and no functions or storage:

- `enum atom_master_data_table_id` enumerates data-table IDs: utility pipeline, multimedia info, firmware info, LCD info, SMU info, VRAM usage by firmware, GPIO pin LUT, GFX info, powerplay info, display object info, indirect IO access, UMC info, DCE info, VRAM info, integrated system info, ASIC profiling info, voltage object info, and `VBIOS_DATA_TBL_ID__UNDEFINED`.
- `enum atom_master_command_table_id` enumerates command IDs: ASIC init, DIG encoder control, engine/memory/pixel/DCE clocks, display power gating, CRTC blank/enable/source/timing, external encoder, I2C transaction, GPU clock computation, dynamic memory settings, memory training, set voltage, DIG1 transmitter control, AUX transaction, get voltage info, and `VBIOS_CMD_TBL_ID__UNDEFINED`.

The order is significant: IDs are dense enum values used to map logical IDs onto offsets in the master lists defined in `atomfirmware.h`.

## Control Flow

There is no internal control flow. Consumers use these IDs as switch or index inputs:

- A helper receives a `VBIOS_DATA_TBL_ID__*` value, maps it to the corresponding field in `struct atom_master_list_of_data_tables_v2_1`, and returns the VBIOS offset for that table.
- A command helper receives a `VBIOS_CMD_TBL_ID__*` value, maps it to a field in `struct atom_master_list_of_command_functions_v2_1`, fills the appropriate command parameter structure from `atomfirmware.h`, and invokes the ATOM parser.
- Undefined IDs provide sentinel values for failed lookup or unsupported requests.

## State and Persistence Behavior

The header has no state. The enum values identify persistent firmware tables or parser command functions stored in a VBIOS image. Any state changes occur in the table contents or in hardware after command execution, not in this file.

## Dependencies

The header has only an include guard. It is normally included at the end of `atomfirmware.h`, and its enum values are meaningful only when kept in sync with `atom_master_list_of_data_tables_v2_1` and `atom_master_list_of_command_functions_v2_1`.

## Integration Points

Primary integration is through `atomfirmware.h` and AMDGPU ATOM firmware helper code. It supports higher-level code that wants to ask for firmware info, VRAM info, GPIO LUT, display object info, SMC DPM info, or a parser command without hard-coding the master-list field layout at every call site.

## Risks and Edge Cases

- Enum order is an ABI convention. Inserting a new ID in the middle without updating all mapping code can redirect a request to the wrong VBIOS table.
- The command enum contains the historical spelling `VBIOS_CMD_TBL_ID__EXTENAL_ENCODER_CONTROL`; fixing the spelling without aliases would break references.
- This file does not encode table revisions. A successful ID lookup still requires the caller to validate `format_revision`, `content_revision`, and `structuresize` before casting the payload.
- `UNDEFINED` values must not be allowed to index a master list.

## Test Signals

- Build tests catch missing enum names used by firmware helper code.
- Unit-style tests for ATOM table lookup should verify each data/command ID resolves to the intended master-list field.
- Negative tests should ensure `*_UNDEFINED` and out-of-range IDs fail cleanly.
- VBIOS integration tests should pair ID lookup with revision/size validation of the resulting table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmwareid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/beige_goby_ip_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/beige_goby_ip_offset.h

## Purpose

`beige_goby_ip_offset.h` is a generated ASIC register-base map for the Beige Goby AMDGPU family. It names the MMIO base segments for each major IP block and publishes both structured `static const struct IP_BASE` tables and preprocessor constants for every instance/segment slot. Downstream register headers and SOC15-style access macros use these bases to translate symbolic IP/register offsets into physical MMIO addresses for this ASIC.

## Important APIs, Types, and Macros

The header exports constants and two small layout types:

- `MAX_INSTANCE` is `7`; `MAX_SEGMENT` is `6`.
- `struct IP_BASE_INSTANCE { unsigned int segment[MAX_SEGMENT]; }` stores the segment bases for one IP instance.
- `struct IP_BASE { struct IP_BASE_INSTANCE instance[MAX_INSTANCE]; }` stores all possible instances for an IP block.
- `static const struct IP_BASE <IP>_BASE` tables cover `ATHUB`, `CLK`, `DBGU_IO0`, `DF`, `DIO`, `DCN`, `DPCS`, `FUSE`, `GC`, `HDA`, `HDP`, `MMHUB`, `MP0`, `MP1`, `NBIO`, `OSSSYS`, `PCIE0`, `SDMA0`, `SMUIO`, `THM`, `UMC`, and `VCN0`.
- `#define <IP>_BASE__INST<n>_SEG<m>` mirrors every structured entry as a macro, including zero-filled unused instance/segment slots.

Notable base shapes:

- `CLK_BASE` has seven populated instances with two populated segments per instance.
- `DBGU_IO0_BASE` has two populated instances.
- `UMC_BASE` has two populated instances.
- Most blocks populate only instance 0.
- `NBIO_BASE` and `PCIE0_BASE` share the same six populated segment bases.
- `GC_BASE` and `SDMA0_BASE` share the same four populated segment bases.
- `DCN_BASE` and `DPCS_BASE` share a five-segment map.
- `SMUIO_BASE` has four populated segments for instance 0.

## Control Flow

There is no executable control flow. Runtime behavior occurs when AMDGPU register-access helpers select an IP block, instance, and segment/base index:

- Generated offset headers provide a register offset within an IP segment.
- ASIC-specific code or macros combine the selected base from this header with the register offset.
- MMIO read/write helpers access the resulting address.

The structured tables support indexed lookup, while the macros support compile-time expansion in generated register definitions.

## State and Persistence Behavior

The header has no runtime state. The `static const` tables are immutable per translation unit. The values describe hardware address-map state fixed for the Beige Goby ASIC; they do not persist driver state and are not modified by the driver.

## Dependencies

The header is standalone except for the C compiler and its include guard. It is meaningful only when used with Beige Goby-compatible generated register offset and mask headers and AMDGPU register access helpers. Its type names (`IP_BASE`, `IP_BASE_INSTANCE`) are also used by sibling ASIC offset headers, so include ordering must avoid conflicting duplicate definitions in a single translation unit.

## Integration Points

The direct references in this tree are mainly generated-header-level rather than C call sites. It parallels `sienna_cichlid_ip_offset.h` and other ASIC base maps and is part of the generated register infrastructure used by AMDGPU IP implementations for GC, SDMA, SMUIO, NBIO/PCIE, UMC, VCN, DCN/DPCS, thermal, clock, and firmware/SMU blocks.

Beige Goby support elsewhere appears through firmware names and SMU powerplay table handling, including `beige_goby_*` firmware modules and `PPTable_beige_goby_t`; those consumers rely on matching register base maps when accessing hardware.

## Risks and Edge Cases

- A wrong base segment redirects MMIO access to the wrong hardware block. This can cause silent misconfiguration, hangs, failed firmware loads, or register reads that look valid but describe another block.
- Zero entries are placeholders for absent instances or segments, not necessarily valid address zero. Consumers must know whether an instance exists before using a slot.
- The structured `static const` definitions in a header create one internal-linkage copy per translation unit. That is usually acceptable for generated base maps but should not be converted to external definitions without coordinating all ASIC headers.
- `MAX_SEGMENT` is 6 for Beige Goby, while sibling headers may use fewer segments. Generic code must use the header's own dimensions.
- Some IP blocks intentionally alias base maps (`NBIO`/`PCIE0`, `GC`/`SDMA0`, `DCN`/`DPCS`, `MP0`/`MP1`). Treating that as accidental duplication and changing one side can break block-specific access paths.

## Test Signals

- Build coverage for Beige Goby ASIC support catches missing base symbols.
- Register smoke tests should read known ID/status registers from each populated IP block and compare against expected values.
- Firmware loading tests for GFX, SDMA, VCN, PSP/SMU, and DMUB provide broad indirect coverage of the base map.
- Suspend/resume, reset, clock-gating, and power-management tests are useful because they touch many IP blocks through these bases.
- Address-map comparison against generated register database output or known-good MMIO traces is the strongest regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/beige_goby_ip_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cgs_common.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cgs_common.h

## Purpose

`cgs_common.h` defines the common services interface used by AMDGPU subsystems that need hardware access without depending directly on the full `amdgpu_device` implementation. CGS exposes an opaque `struct cgs_device`, a vtable of MMIO/indirect-register/firmware-info operations, field manipulation macros, and convenience wrappers. It is used by PowerPlay, ACP, Display, and related components as a narrow adapter layer over AMDGPU register and firmware services.

## Important APIs, Types, and Macros

Core types:

- `struct cgs_device` contains `const struct cgs_ops *ops` and is intended to be embedded at the start of a driver-private structure.
- `struct cgs_ops` provides `read_register`, `write_register`, `read_ind_register`, `write_ind_register`, and `get_firmware_info`.
- `struct cgs_firmware_info` returns firmware versioning, image size, MC address, SMC start address, kernel pointer, and kicker status.
- `enum cgs_ind_reg` names indirect spaces: PCIE, SMC, UVD context, DIDT, GC CAC, SE CAC, and audio endpoint.
- `enum cgs_ucode_id` names firmware classes: SMU, SMU SK, SDMA0/1, CP CE/PFP/ME/MEC/MEC JT, GMCON RENG, RLC G, storage, and maximum sentinel.
- `cgs_handle_t` is an unsigned long generic handle.

Register access macros:

- `CGS_REG_FIELD_SHIFT(reg, field)` and `CGS_REG_FIELD_MASK(reg, field)` form generated shift/mask symbol names.
- `CGS_REG_SET_FIELD(orig_val, reg, field, field_val)` updates one field in a register value.
- `CGS_REG_GET_FIELD(value, reg, field)` extracts one field.
- `CGS_WREG32_FIELD(device, reg, field, val)` and `CGS_WREG32_FIELD_IND(device, space, reg, field, val)` read-modify-write direct and indirect registers.
- `CGS_CALL`, `CGS_OS_CALL`, `cgs_read_register`, `cgs_write_register`, `cgs_read_ind_register`, `cgs_write_ind_register`, and `cgs_get_firmware_info` dispatch through the vtable.

## Control Flow

The header's control flow is macro-based dispatch:

- A subsystem stores or receives an opaque `struct cgs_device *`.
- A wrapper such as `cgs_read_register(dev, offset)` expands to `CGS_CALL(read_register, dev, offset)`.
- `CGS_CALL` casts the opaque pointer to `struct cgs_device *` and calls the selected function pointer from `ops`.
- Field write helpers perform a read-modify-write sequence using either direct MMIO or a selected indirect register space.
- Firmware queries call `get_firmware_info` with a `cgs_ucode_id` and fill `struct cgs_firmware_info`.

The concrete implementation in this tree is `amdgpu_cgs.c`, where `struct amdgpu_cgs_device` embeds `struct cgs_device` and forwards operations to AMDGPU register and firmware helpers.

## State and Persistence Behavior

The header defines no storage. Runtime state is held by the concrete object embedding `struct cgs_device` and by hardware:

- Register reads/writes affect GPU MMIO state immediately.
- Indirect register operations affect the selected indirect register space.
- Firmware info points to loaded firmware metadata and may include a CPU pointer to firmware image data.
- The `ops` pointer must remain valid for the lifetime of every user of the CGS device.

## Dependencies

The header includes `amd_shared.h` for shared AMD types and depends on fixed-width integer and boolean definitions from the kernel build environment. It expects generated register headers to define `mm<reg>`, `ix<reg>`, `<reg>__<field>__SHIFT`, and `<reg>__<field>_MASK` symbols used by the field macros. `CGS_OS_CALL` assumes an `os_ops` member exists in an OS-specific extension, although `struct cgs_device` here only defines `ops`.

## Integration Points

Representative users include:

- `amdgpu/amdgpu_cgs.c`, which creates and destroys CGS devices and implements the vtable.
- `amdgpu/amdgpu_acp.c` and `acp/acp_hw.c`, which use CGS for ACP register access.
- `display/amdgpu_dm/*` and Display Core initialization, which pass CGS access into display code.
- PowerPlay hwmgr/smumgr code such as `vega10_hwmgr.c`, `vega20_processpptables.c`, `smu7_hwmgr.c`, and related files.

## Risks and Edge Cases

- `ops` is not checked for NULL by wrapper macros. Callers must ensure the CGS device is fully initialized and not destroyed.
- Field write macros perform read-modify-write without locking. Concurrent access to the same register can lose updates unless higher layers serialize.
- `CGS_WREG32_FIELD` and `CGS_WREG32_FIELD_IND` shift `val` but do not explicitly mask it after shifting. Out-of-range field values can leak into adjacent bits.
- Direct and indirect offsets are compile-time macro conventions. Passing a generated symbol from the wrong IP/version header can access the wrong register.
- `CGS_OS_CALL` references `os_ops`, which is not present in the common struct definition. It must only be used with an OS-specific compatible extension.
- Firmware info pointers and MC addresses are only valid according to the owning firmware loader's lifetime rules.

## Test Signals

- Build tests across AMDGPU, Display, ACP, and PowerPlay catch vtable and macro signature mismatches.
- Register read/write smoke tests through CGS should match direct AMDGPU helper behavior.
- Field macro tests should validate `CGS_REG_SET_FIELD`/`GET_FIELD` for representative generated masks and boundary values, including out-of-range inputs.
- Firmware loading tests should verify every `cgs_ucode_id` used by a platform returns expected version, size, address, and pointer data or a clean error.
- Concurrency-sensitive tests around power management and display mode setting can expose read-modify-write races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cgs_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cik_structs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cik_structs.h

## Purpose

`cik_structs.h` defines packed-by-convention C structs that mirror Sea Islands/CIK hardware queue context images used by AMD KFD and SDMA queue management. It provides the memory layout for a CIK compute MQD (memory queue descriptor) and an SDMA RLC register save/restore block. The file contains no logic; correctness depends on the field order matching the hardware/kernel queue programming ABI.

## Important APIs, Types, and Macros

The header exports two structs:

- `struct cik_mqd` is the CIK compute queue descriptor. It contains compute dispatch dimensions, program/TBA/TMA addresses, program resources, VMID, resource limits, static thread-management masks, trap/TMP ring settings, user data SGPR fields, HQD queue state, queue base/rptr/wptr/report/poll addresses, doorbell control, queue/IB controls, dequeue and semaphore fields, atomic preop fields, MQD timing/query/connect accounting fields, IQ timer packet data, reserved gaps, and sixteen queue doorbell IDs.
- `struct cik_sdma_rlc_registers` mirrors SDMA RLC queue register state: ring buffer control/base/read/write pointers, write-pointer polling and report addresses, IB state, skip/context/doorbell/virtual-address fields, APE1/doorbell log, reserved padding through index 125, and driver-internal `sdma_engine_id` plus `sdma_queue_id` in the final two slots.

There are no helper functions, enums, or macros beyond the include guard.

## Control Flow

The header has no internal control flow. Runtime flow is implemented in KFD queue management:

- CIK KFD code allocates GTT memory sized to `sizeof(struct cik_mqd)` and aligned as required by hardware.
- It zeroes the MQD, fills fields from `queue_properties`, maps queue ring and write-pointer report addresses, programs VMID/doorbell/HQD fields, and passes the MQD to HIQ/HQD load paths.
- Queue update paths modify selected MQD fields, while dump/debug paths copy out `sizeof(struct cik_mqd)`.
- SDMA queue management can save or restore the SDMA RLC register image using `struct cik_sdma_rlc_registers`.

## State and Persistence Behavior

Instances of these structs are runtime state objects, usually allocated in GPU-accessible memory or used as CPU-side snapshots:

- `struct cik_mqd` persists for the lifetime of a compute queue and represents both software-owned queue metadata and hardware-consumed HQD state.
- Queue pointer fields track ring/IB progress and write-pointer polling/reporting.
- Doorbell IDs bind user-mode or kernel queue writes to a hardware queue.
- The SDMA RLC register block persists as a save/restore image; the last two fields are explicitly repurposed for driver-internal engine and queue identity rather than hardware registers.

The header itself persists no data.

## Dependencies

The file assumes `uint32_t` is available from the includer or kernel build environment. It is consumed by CIK-specific KFD code and must match CIK CP/HQD and SDMA register definitions. No external headers are included.

## Integration Points

Primary direct consumer:

- `drivers/gpu/drm/amd/amdkfd/kfd_mqd_manager_cik.c`

That code casts MQD memory to `struct cik_mqd`, initializes fields, updates queue properties, checks queue activity, destroys MQDs, dumps MQD contents, and exposes `mqd_size = sizeof(struct cik_mqd)` through CIK MQD manager operations.

## Risks and Edge Cases

- Field order and size are hardware ABI. Adding padding, changing types, or reordering fields will corrupt queue descriptors.
- The structure is not explicitly packed, so it relies on all fields being `uint32_t` and naturally contiguous. Introducing smaller or larger fields would change layout.
- MQD memory must satisfy hardware alignment and accessibility requirements; the consumer aligns allocation to 256 bytes.
- Reserved fields are intentional layout placeholders. Removing or reusing them can shift later hardware fields.
- The final SDMA fields are driver-internal repurposed reserved slots. Treating them as hardware state during raw save/restore could leak software metadata into assumptions about register images.
- Doorbell, VMID, queue base, and pointer fields are security-sensitive. Incorrect values can cause queue hangs or cross-process memory access faults.

## Test Signals

- Compile KFD CIK support and verify `sizeof(struct cik_mqd)` remains the expected MQD size used by `kfd_mqd_manager_cik.c`.
- Queue creation, update, eviction/restore, and destruction tests on CIK hardware validate the MQD layout.
- KFD compute dispatch tests exercise program address, resource, ring, VMID, doorbell, and HQD fields.
- Queue dump/debug paths should copy exactly `sizeof(struct cik_mqd)` without truncation.
- SDMA queue tests should validate ring pointer progression and save/restore behavior, including preservation of driver-internal engine/queue IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/cik_structs.h -->
