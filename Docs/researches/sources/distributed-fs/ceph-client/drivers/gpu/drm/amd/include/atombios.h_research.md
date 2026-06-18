# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atombios.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003485`: lines 1-5123, `Docs/researches/chunks/subset-b-003485_research.md`
- `subset-b-003486`: lines 5124-9309, `Docs/researches/chunks/subset-b-003486_research.md`

## Chunk Research

### subset-b-003485: lines 1-5123

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atombios.h lines 1-5123

## Scope And Purpose

This chunk is the first 5,123 lines of AMD's `atombios.h` ABI header. It is not Ceph filesystem code despite living under the `ceph-client` source mirror. It defines the packed binary contracts shared by AMD GPU VBIOS/ATOMBIOS firmware, the kernel ATOM interpreter, display code, and power-management code.

The file is declarative: it exports constants, packed table layouts, command parameter blocks, versioned data-table structures, bitfield views, and backward-compatibility aliases. It defines no executable functions, locks, allocations, or direct MMIO operations. Runtime behavior happens when driver code parses these structures out of the BIOS image or passes the command parameter structures into ATOM command-table execution.

This requested range starts at the license and include guard and reaches into the voltage object table definitions. Later voltage object V3 payload variants continue after line 5123, so this chunk should not be treated as the complete voltage-object section.

## Important APIs, Types, And Tables

The most important contract is binary layout. `#pragma pack(1)` forces byte alignment for BIOS data, and the header requires `ATOM_BIG_ENDIAN` to be defined so bitfield ordering is explicit. Core scalar names such as `UCHAR`, `USHORT`, `ULONG` are expected from the including environment, with `_H2INC` fallbacks.

Top-level ROM/table structures:

- `ATOM_COMMON_TABLE_HEADER` prefixes most command and data tables with size, format revision, and content revision.
- `ATOM_ROM_HEADER` and `ATOM_ROM_HEADER_V2_1` describe the firmware signature, PCI/runtime offsets, master command table offset, master data table offset, and, in v2.1, PSP directory offset.
- `ATOM_MASTER_LIST_OF_COMMAND_TABLES` and `ATOM_MASTER_COMMAND_TABLE` define command-table slots such as `ASIC_Init`, `SetEngineClock`, `SetMemoryClock`, `SetPixelClock`, `EnableCRTC`, `DIGxEncoderControl`, transmitter control, I2C/AUX transactions, voltage, spread spectrum, SMC init, and DCE clock setup.
- `ATOM_MASTER_LIST_OF_DATA_TABLES` and `ATOM_MASTER_DATA_TABLE` define data-table slots such as `FirmwareInfo`, `LCD_Info`, `GPIO_I2C_Info`, `VRAM_UsageByFirmware`, `GFX_Info`, `PowerPlayInfo`, `Object_Header`, `VRAM_Info`, `IntegratedSystemInfo`, `VoltageObjectInfo`, and `ServiceInfo`.

Clock, PLL, and power command parameter APIs:

- `COMPUTE_MEMORY_ENGINE_PLL_PARAMETERS` through `_V5`, `COMPUTE_GPU_CLOCK_INPUT/OUTPUT_PARAMETERS_V1_6` and `_V1_7`, and `COMPUTE_MEMORY_CLOCK_PARAM_PARAMETERS_V2_1` through `_V2_3` carry memory, engine, SCLK, DFS, MPLL/SPLL, divider, fractional divider, and strobe/performance-mode data.
- `SET_ENGINE_CLOCK_PARAMETERS`, `SET_MEMORY_CLOCK_PARAMETERS`, `ASIC_INIT_PARAMETERS`, `DYNAMIC_CLOCK_GATING_PARAMETERS`, `ENABLE_DISP_POWER_GATING_PARAMETERS_V2_1`, and related `*_PS_ALLOCATION` wrappers model command-table inputs and scratch-space reservations.
- `SET_VOLTAGE_PARAMETERS`, `_V2`, `_V1_3`, `GET_VOLTAGE_INFO_INPUT_PARAMETER_V1_1` through `_V1_3`, and EVV/leakage output structures define voltage control/get queries. Voltage type and mode macros cover VDDC, MVDDC, MVDDQ, VDDCI, VDDGFX, PCC, generic I2C regulators, leakage IDs, EVV voltage lookup, phase setting, and regulator init.

Display and link command parameter APIs:

- DAC, DIG, DVO, LVDS/TMDS, external encoder, transmitter, output-control, blanking, CRTC, overscan, replication, source-select, and timing structures define the command-table surface used by display bring-up and modeset paths.
- `DIG_ENCODER_CONTROL_PARAMETERS` through `_V5` and `DIG_TRANSMITTER_CONTROL_PARAMETERS` through `_V1_6` evolve the ABI across DP link training, DP MST/SST, HBR/HBR2/HBR3-era link rates, DIG front-end selection, UNIPHY selection, lane counts, HPD selection, deep color, and DP lane voltage-swing/pre-emphasis.
- `PIXEL_CLOCK_PARAMETERS` through `_V7`, `SET_DCE_CLOCK_PARAMETERS_V1_1`, and `_V2_1` define PPLL/DCPLL/PHY PLL programming, pixel clock units, HDMI deep color ratios, DPREFCLK/DISPCLK generation, YUV420, dual-link DVI, and PLL reference source selection.
- `ADJUST_DISPLAY_PLL_*`, `ENABLE_SPREAD_SPECTRUM_ON_PPLL*`, `MEMORY_TRAINING_PARAMETERS*`, and legacy LVDS/TMDS/DVO encoder structures round out display PLL, spread-spectrum, memory-training, and pre-DCE3 encoder contracts.

Data-table structures:

- Firmware tables include `ATOM_FIRMWARE_INFO` through `ATOM_FIRMWARE_INFO_V2_2`, firmware capability bitfields, default/maximum clocks, PLL input/output limits, boot voltages, reference clocks, backlight constraints, remote display config, and board branding/cooling metadata.
- Integrated system tables include `ATOM_INTEGRATED_SYSTEM_INFO`, `_V2`, and `_V5`, carrying boot clocks, UMA/SidePort memory clocks, system config flags, CPU type, HT/link information, DDI slot config, UMA channel count, NB voltage data, and display request vectors.
- Display inventory tables include encoder/device indexes, `ATOM_DEVICE_*` support masks, connector type macros, I2C ID configuration, `ATOM_GPIO_I2C_INFO`, mode timing structures, `ATOM_LVDS_INFO`, `ATOM_LVDS_INFO_V12`, `ATOM_LCD_INFO_V13`, spread-spectrum assignments, analog TV info, DPCD info, component video info, and the object table ecosystem.
- Object tables include `ATOM_OBJECT_HEADER`, `ATOM_DISPLAY_OBJECT_PATH`, `ATOM_OBJECT_TABLE`, `ATOM_SRC_DST_TABLE_FOR_ONE_OBJECT`, external display path and connection info, common record headers, I2C/HPD/output-protection/device-tag/GPIO/router/encoder-cap/bracket-layout records, and connector capability records.
- Firmware VRAM reservation structures define fixed offsets and sizes for hardware cursor surfaces, EDID storage, DTD/STD timing areas per display device, DP training scratch space, stack storage, and reservation table versions.
- Voltage table structures in this chunk include `ATOM_VOLTAGE_INFO`, `ATOM_VOLTAGE_FORMULA`, `VOLTAGE_LUT_ENTRY`, `ATOM_VOLTAGE_CONTROL`, `ATOM_VOLTAGE_OBJECT`, `ATOM_VOLTAGE_OBJECT_V2`, `ATOM_VOLTAGE_OBJECT_INFO`, `ATOM_VOLTAGE_OBJECT_INFO_V2`, `ATOM_LEAKID_VOLTAGE`, and `ATOM_VOLTAGE_OBJECT_HEADER_V3`.

## Control Flow And Runtime Behavior

There is no C control flow in this header. The effective control flow is data-driven:

1. Driver startup verifies and parses the ATOMBIOS image using fixed offsets such as `OFFSET_TO_POINTER_TO_ATOM_ROM_HEADER`.
2. The ROM header points to master command and data tables.
3. Parser helpers use table indexes and common headers to locate a table, inspect its format/content revision, and cast the payload to one of these versioned structures.
4. Command callers fill the matching parameter block, then execute the ATOM command table. The firmware bytecode and interpreter mutate hardware state, scratch space, or returned fields.
5. Data-table consumers read firmware tables directly to configure clocks, voltage policy, display topology, panel timing, I2C/DDC routing, VRAM reservations, and board-specific quirks.

The same table slot may use different parameter layouts depending on command-table revision. For example, pixel-clock setup spans v1, v2, v3, v5, v6, and v7 structures; DIG encoder/transmitter control also changes shape across revisions. Correct revision dispatch is therefore part of the runtime contract even though the header itself only defines the shapes.

## State And Persistence Behavior

The header itself stores no mutable software state. It describes state persisted in the GPU VBIOS image and temporary command parameter/scratch buffers.

Persistent firmware state includes ROM header offsets, table revision fields, default clocks, PLL limits, boot voltages, panel timing, object topology, connector records, spread-spectrum assignments, integrated-system settings, GPIO/I2C routing, and voltage-control metadata. Driver state is derived from those tables and cached by AMDGPU/Radeon mode, power, and ATOM parser code.

Some tables describe persistent or reserved memory regions in VRAM. The VRAM usage definitions reserve hardware cursor, EDID, mode timing, DP training, and command-table scratch areas, and `ATOM_VRAM_USAGE_BY_FIRMWARE` reports firmware-owned framebuffer regions to the driver. Incorrect interpretation can collide with firmware or display scratch memory.

Command parameter blocks are transient, but many commands program durable hardware state: clocks, PLLs, display pipes, encoders, transmitters, power gating, voltage regulators, spread spectrum, backlight state, and memory training/self-refresh state. The table revisions and action constants determine whether a parameter is input, output, or both.

## Dependencies And Integration Points

This header depends on the ATOM parser/interpreter and on AMD display and power-management users respecting the packed binary ABI. In this tree, relevant consumers include:

- Radeon ATOM parser and execution infrastructure in `drivers/gpu/drm/radeon/atom.c` and `drivers/gpu/drm/radeon/atom.h`, which parse master tables and execute command tables.
- Radeon display paths such as `radeon/atombios_crtc.c`, `radeon/atombios_encoders.c`, `radeon/atombios_dp.c`, `radeon/atombios_i2c.c`, and `radeon/radeon_atombios.c`, which use pixel-clock, CRTC, encoder, transmitter, object-table, panel, firmware, VRAM, and voltage structures.
- AMDGPU power-management code including `amd/pm/legacy-dpm/*.c` and newer SMU users through `amdgpu_atombios.h`, which parse firmware data tables and execute ATOM tables for clocks, voltage, and board metadata.
- External headers such as `objectid.h` and ASIC-specific register/code paths provide connector, encoder, transmitter, and register meanings referenced by comments and object IDs.

The command and data table slot order is an ABI. Comments repeatedly warn that certain offsets and table positions must not change because firmware and drivers address them by table index rather than by name.

## Risks And Edge Cases

- Packed layout is mandatory. Any compiler packing, type-width, or endian-bitfield mismatch corrupts all downstream parsing.
- Many structures are revisioned but share names and table slots. Selecting the wrong version can misread fields while still compiling cleanly.
- Flexible arrays and variable-length records, such as object tables, GPIO pin LUTs, fake EDID records, connector device tags, display paths, and bracket layout records, require size/header validation before walking.
- Several structures overlay input and output fields through unions. Callers must know the command action and revision before interpreting returned data.
- Clock and voltage units vary: many clocks use 10 kHz, some newer pixel clocks use 100 Hz, voltage may be mV or 0.01 mV, and DP link rates are sometimes encoded as raw IDs or multiples of 270 MHz.
- Backward-compatibility aliases map old table names to newer slots. This is useful for old code, but it can obscure which firmware table is actually being called.
- Display link setup is highly version-sensitive. Wrong `DIG_ENCODER_CONTROL`, `DIG_TRANSMITTER_CONTROL`, `PIXEL_CLOCK`, or `SET_DCE_CLOCK` packing can break DP training, HDMI deep color, eDP panels, dual-link DVI, MST, HPD routing, or PLL selection.
- Object-table records use small record type and size fields. A malformed BIOS can cause bad topology, I2C, HPD, GPIO, or router interpretation if consumers do not bounds-check each record.
- Firmware VRAM reservation constants and tables protect memory shared with BIOS/ATOM command execution. Incorrect sizes or addresses can corrupt EDID, timing, DP training, cursor, or scratch data.
- The requested range ends mid voltage-object family. Any complete analysis of voltage object V3 behavior must include later lines.

## Test Signals

Useful validation for this chunk includes:

- Build coverage for AMDGPU/Radeon users that include `atombios.h`, especially ATOM parser, display, DP, I2C, legacy DPM, and SMU-facing code.
- Static checks that `sizeof()` and `offsetof()` for key packed structs match expected firmware ABI sizes for known BIOS revisions.
- Parser tests or ROM-fixture tests that walk `ATOM_ROM_HEADER`, master command/data tables, firmware info, object headers, GPIO/I2C info, LCD info, VRAM usage, and voltage info with bounds checking.
- Runtime modeset coverage across CRT/DAC, LVDS/eDP, DVI, HDMI, DP SST, DP MST, deep color, HBR2/HBR3-capable connectors, backlight control, HPD, DDC/AUX, suspend/resume, and multi-display topologies.
- Power-management coverage for ASIC init, engine/memory clock changes, memory self-refresh, spread spectrum, voltage get/set, leakage/EVV lookup, and VRAM reservation handling.
- Negative testing with absent tables, zero offsets, unknown table revisions, short table sizes, malformed object records, no-I2C devices, and unsupported command-table revisions.

## Cross-Chunk Notes

This chunk starts at the beginning of `atombios.h`, so there is no earlier chunk needed to understand the header prologue. It stops at `VOLTAGE_OBJ_HIGH_STATE_LEAKAGE_LUT`; later lines define additional voltage object V3 payloads and other data tables. The final per-file report should merge those later chunks before making complete claims about voltage objects or the full ATOMBIOS table namespace.

### subset-b-003486: lines 5124-9309

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atombios.h lines 5124-9309

Chunk id: `subset-b-003486`

## Purpose

This chunk defines a large part of the legacy AMD ATOM BIOS ABI used by the DRM AMDGPU stack. It is almost entirely declarative: packed C structs, unions, bit masks, command-table parameter layouts, table aliases, and compatibility macros that describe how the kernel should parse VBIOS data tables and invoke ATOM command tables. The covered range spans voltage objects and ASIC profiling, APU integrated system information, spread-spectrum setup, BIOS scratch-register state, table revision helpers, VBIOS-only command parameters, memory-controller and VRAM module descriptions, VESA/VBE structures, display output and DP/I2C service parameters, DIG transmitter analog-setting tables, ROM/ACPI VFCT headers, obsolete supported-device tables, and legacy PowerPlay tables.

The practical purpose is to keep the Linux driver binary-compatible with many generations of AMD VBIOS images. Runtime code maps raw ROM/data-table bytes onto these layouts, checks table revisions, converts little-endian fields, and then configures clocks, voltage limits, display routing, memory controller timing, DP AUX, I2C, backlight/LVDS/eDP behavior, and power-management defaults.

## Important APIs, Types, and Constants

### Voltage and ASIC Profiling

- `ATOM_I2C_VOLTAGE_OBJECT_V3`, `ATOM_GPIO_VOLTAGE_OBJECT_V3`, `ATOM_LEAKAGE_VOLTAGE_OBJECT_V3`, `ATOM_SVID2_VOLTAGE_OBJECT_V3`, `ATOM_EVV_VOLTAGE_OBJECT_V3`, and union `ATOM_VOLTAGE_OBJECT_V3` describe VBIOS voltage-control objects for I2C regulators, GPIO voltage lookup, leakage-id lookup, SVID2 rails, and EVV DPM voltage adjustment data. Flexible arrays such as `asVolI2cLut[]`, `asVolGpioLut[]`, and `asLeakageIdLut[]` require callers to use table/header sizes rather than `sizeof`.
- `ATOM_VOLTAGE_OBJECT_INFO_V3_1` groups up to three voltage objects. Voltage-object mode constants include `VOLTAGE_OBJ_*` definitions from earlier in the file plus chunk-local data-size flags `VOLTAGE_DATA_ONE_BYTE` and `VOLTAGE_DATA_TWO_BYTE`.
- `ATOM_ASIC_PROFILING_INFO`, `ATOM_ASIC_PROFILING_INFO_V2_1`, and `ATOM_ASIC_PROFILING_INFO_V3_1` through `V3_6` define fuse-derived voltage/leakage/speed-model/AVFS parameters. Important subtypes are `EFUSE_LOGISTIC_FUNC_PARAM`, `EFUSE_LINEAR_FUNC_PARAM`, and `ATOM_ASIC_PROFILE_VOLTAGE`.
- `ATOM_ASIC_PROFILING_INFO_V3_6` is significant for Polaris AVFS. AMD powerplay code reads it in `ppatomctrl.c` to populate AVFS mean/sigma, GB Vdroop, fuse-table, load-line, TDC, and no-calc voltage fields, and to derive min/max VDDC for Polaris-class chips.

### SMU, GFX, Power Source, and Clock/Voltage Capability

- `ATOM_SCLK_FCW_RANGE_ENTRY_V1`, `ATOM_SMU_INFO_V2_1`, and `ATOM_GFX_INFO_V2_1`/`V2_3` define SMU clock control and GFX IP topology/leakage-table pointers for Polaris-era parts.
- `ATOM_POWER_SOURCE_OBJECT` and `ATOM_POWER_SOURCE_INFO` describe PCIe/6-pin/8-pin power-source sensing via GPIO or I2C, with constants such as `POWERSOURCE_6PIN_CONNECTOR_ID1`, `POWER_SENSOR_GPIO`, and `POWER_SENSOR_I2C`.
- `ATOM_CLK_VOLT_CAPABILITY`, `ATOM_CLK_VOLT_CAPABILITY_V2`, and `ATOM_AVAILABLE_SCLK_LIST` map clocks to voltage indexes/levels. These are embedded in integrated-system-info tables and consumed by display/power code to translate BIOS 10 kHz clock units into driver kHz fields.

### Integrated System Info and Fusion Tables

- `ATOM_INTEGRATED_SYSTEM_INFO_V6` covers Llano/Ontario APU system data, followed by `ATOM_FUSION_SYSTEM_INFO_V1`.
- `ATOM_TDP_CONFIG_BITS`/`ATOM_TDP_CONFIG` define endian-sensitive bitfields for original TDP, configurable TDP override, and cTDP enable state.
- `ATOM_INTEGRATED_SYSTEM_INFO_V1_7`, `V1_8`, `V1_9`, and `V1_10` track Trinity, Kaveri/Kabini, Carrizo, and later APU data. They add or repurpose fields for VBIOS miscellaneous flags, GPU capability flags, display-clock voltage mappings, reserved GPU system memory, NB P-state clocks/voltages, PSP version, eDP voltage-swing mode, HDMI redriver I2C settings, and camera data.
- `ATOM_FUSION_SYSTEM_INFO_V2` and `V3` embed integrated-system-info plus reserved PowerPlay table storage; `FUSION_V3_OFFSET_FROM_TOP_OF_FB` fixes a firmware framebuffer offset.
- Integration signals: `smu8_hwmgr.c` fetches `ATOM_INTEGRATED_SYSTEM_INFO_V1_9` with `smu_atom_get_data_table()`, requires content revision 9, and stores boot clocks; `bios_parser.c` parses the same layout for display integrated info and converts 10 kHz units to kHz; `amdgpu_atombios.c` also declares/use-copies v1.9 fields.

### Spread Spectrum, I2C Device Setup, and Scratch State

- `ATOM_I2C_DATA_RECORD`, `ATOM_I2C_DEVICE_SETUP_INFO`, and `ATOM_ASIC_MVDD_INFO` define I2C programming records for external spread-spectrum or memory-voltage devices.
- `ATOM_ASIC_SS_ASSIGNMENT`, `ATOM_ASIC_SS_ASSIGNMENT_V2`, `ATOM_ASIC_SS_ASSIGNMENT_V3`, and corresponding `ATOM_ASIC_INTERNAL_SS_INFO*` table structs describe internal/external spread-spectrum targets for memory, engine, UVD, TMDS, HDMI, LVDS, DP, DCPLL, VCE, and GPUPLL. `SS_MODE_V3_*` masks encode center spread, external SS, and percentage divisor interpretation.
- BIOS scratch definitions `ATOM_S0_*` through `ATOM_S9_*` map shared scratch registers to device connection, ROM location, TV standard, active device/CRTC state, LCD panel state, DOS requests, ACPI events, DOS mode state, and I2C busy/completion/abort state. Byte-aligned aliases mirror the same state for BIOS code.
- Action macros such as `SET_ATOM_S6_DEVICE_CHANGE`, `CLEAR_ATOM_S6_LID_STATE`, and `SET_ATOM_S7_DOS_8BIT_DAC_EN` combine a scratch index, bit shift, and set/clear flag for command-table style scratch manipulation.

### Driver Macros and Command-Table Parameter Layouts

- `GetIndexIntoMasterTable(MasterOrData, FieldName)` computes a master table index from an `ATOM_MASTER_LIST_OF_*_TABLES` member offset. It has separate C and C++ implementations.
- `GET_COMMAND_TABLE_COMMANDSET_REVISION`, `GET_COMMAND_TABLE_PARAMETER_REVISION`, `GET_DATA_TABLE_MAJOR_REVISION`, and `GET_DATA_TABLE_MINOR_REVISION` extract revision nibbles from `ATOM_COMMON_TABLE_HEADER`. Call sites such as `ppatomctrl.c` use these macros to choose VRAM/MC parsing paths.
- VBIOS command parameter structs include `MEMORY_PLLINIT_PARAMETERS`, `GPIO_PIN_CONTROL_PARAMETERS`, `ENABLE_SCALER_PARAMETERS`, `ENABLE_HARDWARE_ICON_CURSOR_PARAMETERS`, `ENABLE_GRAPH_SURFACE_PARAMETERS*`, `MEMORY_CLEAN_UP_PARAMETERS`, `GET_DISPLAY_SURFACE_SIZE_PARAMETERS*`, `PALETTE_DATA_CONTROL_PARAMETERS_V3`, `INTERRUPT_SERVICE_PARAMETER_V2`, `READ_EFUSE_VALUE_PARAMETER`, `INDIRECT_IO_ACCESS`, and `ATOM_OEM_INFO`.
- These parameter layouts are passed to `amdgpu_atom_execute_table()`/ATOM parser equivalents as raw table arguments, so field order and byte packing are ABI-critical.

### Memory Controller, VRAM, and Memory Training

- `ATOM_INIT_REG_BLOCK`, `ATOM_INIT_REG_INDEX_FORMAT`, `ATOM_MEMORY_SETTING_ID_CONFIG(_ACCESS)`, and `ATOM_MEMORY_SETTING_DATA_BLOCK` describe register-index lists and per-clock/per-memory register data blocks. Constants like `END_OF_REG_INDEX_BLOCK`, `END_OF_REG_DATA_BLOCK`, `VALUE_DWORD`, and `ACCESS_PLACEHOLDER` define embedded bytecode/data encodings.
- `ATOM_MC_INIT_PARAM_TABLE` and `ATOM_MC_INIT_PARAM_TABLE_V2_1` describe memory-controller init offsets, MCU code location/length, and MC register-init tables. `MCuCodeHeader`, `UCODE_ROM_START_ADDRESS`, and `UCODE_SIGNATURE` describe GDDR5 MC microcode blocks.
- Memory density/vendor constants such as `_64Mx32`, `_512Mx8`, `SAMSUNG`, `HYNIX`, and `MICRON` are used inside VRAM module descriptors.
- `ATOM_VRAM_MODULE_V1` through `V8`, `ATOM_MEMORY_FORMAT`, and `ATOM_MEMORY_TIMING_FORMAT` through `V2` capture memory topology, channel mapping, rank/burst/density, voltage defaults, timing tables, GDDR fields, part-number strings, and memory-size units. `ATOM_VRAM_MODULE` aliases to V3 in this chunk, while newer table headers use explicit V7/V8.
- `ATOM_VRAM_INFO_V2`, `V3`, `V4`, `ATOM_VRAM_INFO_HEADER_V2_1`, and `V2_2` provide top-level VRAM table headers and offsets to register-adjust, per-byte/per-tile, PHY init, and DRAM data remap tables. `ATOM_DRAM_DATA_REMAP` maps DRAM byte/bit lanes to GPU lanes.
- Integration signal: `ppatomctrl.c` casts VRAM info to `ATOM_VRAM_INFO_HEADER_V2_2`, validates `ucNumOfVRAMModule` and format revision, offsets into `usMemClkPatchTblOffset`, and feeds `ATOM_INIT_REG_BLOCK` into memory-controller timing setup.

### VESA/VBE and BIOS Function Codes

- `PTR_32_BIT_STRUCTURE`, `PTR_32_BIT_UNION`, `VBE_1_2_INFO_BLOCK_UPDATABLE`, `VBE_2_0_INFO_BLOCK_UPDATABLE`, `VBE_INFO_BLOCK`, `VBE_FP_INFO`, and `VESA_MODE_INFO_BLOCK` mirror VBE info/mode blocks, including banked/linear framebuffer fields and direct-color masks.
- `ATOM_BIOS_FUNCTION_*`, `ATOM_SUB_FUNCTION_*`, and `ATOM_PARAMETER_VESA_DPMS_*` define legacy BIOS interrupt/function codes for DDC, device detect/switch, panel control, video state, lid/thermal/critical notifications, DPMS, and display info update calls.

### Display Output, DP AUX/I2C, DIG Transmitters, and PHY Settings

- `ASIC_TRANSMITTER_INFO`, `ASIC_ENCODER_INFO`, `ATOM_DISP_OUT_INFO`, `ATOM_DISP_OUT_INFO_V2`, `ATOM_DISP_CLOCK_ID`, `ASIC_TRANSMITTER_INFO_V2`, and `ATOM_DISP_OUT_INFO_V3` define display-output table layouts, transmitter/encoder IDs, display clock source offsets, main parser far-call address, DCE revision, display-engine counts, PPLL counts, core reference clock source, and display capability bits.
- `ATOM_DISPLAY_DEVICE_PRIORITY_INFO` supplies BIOS display priority order.
- `PROCESS_AUX_CHANNEL_TRANSACTION_PARAMETERS` and `_V2` are command-table arguments for DP AUX. V2 adds `ucHPD_ID`. `amdgpu/atombios_dp.c` and `radeon/atombios_dp.c` use these structures in a union, copy request data into ATOM scratch memory, fill offsets/line/HPD/delay, execute `ProcessAuxChannelTransaction`, and read `ucReplyStatus`.
- `DP_ENCODER_SERVICE_PARAMETERS`, `_V2`, and `DP_ENCODER_SERVICE_PS_ALLOCATION_V2` support DP sink detection and external connection detection. `DPCD_*_TBL_ADDR` constants describe fixed offsets into the DP training table for link-rate/lane-count, spread-spectrum, voltage swing/pre-emphasis, training pattern, lane status, and AUX DDC operations.
- `PROCESS_I2C_CHANNEL_TRANSACTION_PARAMETERS` plus `HW_I2C_WRITE`, `HW_I2C_READ`, and `I2C_2BYTE_ADDR` describe hardware I2C command-table arguments.
- `ATOM_HW_MISC_OPERATION_*`, `SET_HWBLOCK_INSTANCE_PARAMETER_V2`, and `SELECT_*` constants support miscellaneous HW queries and selecting display engine/PLL/DCIO/DIG/VGA blocks.
- `DIG_TRANSMITTER_INFO_HEADER_V3_1`, `V3_2`, and `V3_3` provide offsets to DP voltage-swing/pre-emphasis settings, PHY analog register lists, PHY PLL settings, DP SS settings, and multiple eDP voltage-swing-mode tables. `CLOCK_CONDITION_*`, `PHY_CONDITION_*`, and `PHY_ANALOG_SETTING_INFO(_V2)` describe variable-length conditional register/value arrays.
- `GFX_HAVESTING_PARAMETERS` describes CU/RB/PRIM harvesting requests.

### ROM, ACPI VFCT, Obsolete Tables, and Compatibility Aliases

- `VBIOS_ROM_HEADER` maps the PCI ROM header and offsets to PCI data structures, core handlers, timestamps, and ATOM BIOS message data.
- `MC_MISC0__MEMORY_TYPE_*` and `ATOM_MEM_TYPE_*_STRING` map VBIOS MC scratch memory-type bits to display strings, including GDDR5, HBM, and DDR3.
- Obsolete/legacy definitions include `ATOM_DAC_INFO`, `COMPASSIONATE_DATA`, `ATOM_SUPPORTED_DEVICES_INFO*`, `ATOM_TMDS_INFO`, `DVO_ENCODER_CONTROL_PARAMETERS`, `ATOM_XTMDS_INFO`, `DFP_DPMS_STATUS_CHANGE_PARAMETERS`, and legacy `ATOM_POWERPLAY_INFO*`/`ATOM_POWERMODE_INFO*`.
- Compatibility aliases remap older table names, command names, output-control parameter names, and DFP/TV device bits to newer identifiers. They reduce churn across VBIOS/DAL/driver naming transitions but also allow obsolete names to remain visible.
- `ATOM_SERVICE_INFO` and related service/hole structs, followed by `UEFI_ACPI_VFCT`, `GOP_VBIOS_CONTENT`, and `GOP_LIB1_CONTENT`, describe signed-service holes and AMD ACPI VFCT GOP image containers. The file temporarily resets and re-enables packing around these ABI records, then ends the header and includes `pptable.h`.

## Control Flow and Data Flow

This header does not implement executable control flow. Runtime flow is external:

1. Driver code locates a data or command table through the ATOM master table, commonly using `GetIndexIntoMasterTable(DATA, ...)` or `GetIndexIntoMasterTable(COMMAND, ...)`.
2. The ATOM BIOS parser or helper returns a pointer into the VBIOS image or an ATOM scratch buffer.
3. The caller selects a chunk-defined struct according to table format/content revision, ASIC family, or command revision.
4. The caller interprets raw fields with explicit endianness conversion (`le16_to_cpu`, `le32_to_cpu`) and units conversion, commonly BIOS 10 kHz to kHz, 0.01 mV/0.25 mV voltage scales, or 4 ms LVDS sequence steps.
5. For command tables, the caller fills a packed parameter struct, executes the ATOM command interpreter, then reads output fields or scratch-memory results.
6. Variable-length arrays and offset fields require pointer arithmetic from the table base. Examples include VRAM register patch blocks, DIG PHY analog setting arrays, spread-spectrum assignment arrays, I2C data records, and GOP/VFCT image payloads.

The chunk therefore defines contracts rather than algorithms. The algorithms live in ATOM parser, display, powerplay, memory-controller, and DP/I2C code.

## State and Persistence Behavior

- Persistent state comes from firmware: VBIOS data tables, ROM headers, ACPI VFCT records, MC microcode blobs, and table-internal offsets. The kernel should treat these as immutable firmware inputs.
- Shared runtime state is represented by BIOS scratch-register masks (`ATOM_S0_*` through `ATOM_S9_*`). These bits encode connection state, active display devices, CRTC assignment, LCD panel information, requested DOS/ACPI changes, lid/dock/thermal/power events, I2C busy/completed/aborted state, DPMS, current brightness, rotation, and ASIC init completion. Some fields are explicitly firmware-only, but driver-side code may read or update selected scratch bits through command-table interfaces.
- Command-table arguments can be both input and output. Examples include AUX reply status, interrupt status, GPIO readback, EFUSE readback, DP sink type, and HW misc return code.
- Several structures preserve old or reserved fields solely for ABI stability, for example Carrizo integrated-system-info fields marked no longer used but retained to avoid driver build/interface breakage.

## Dependencies and Integration Points

- Depends on earlier definitions in `atombios.h`: scalar aliases (`UCHAR`, `USHORT`, `ULONG`), `ATOM_COMMON_TABLE_HEADER`, master table list types, object/device constants, I2C ID configs, display connector info, DTD formats, command allocation structs, and prior voltage/object/table constants.
- Ends with `#include "pptable.h"`, so the header also integrates with PowerPlay table definitions outside this chunk.
- AMDGPU display integration: `bios_parser.c` consumes integrated-system-info v1.9 and data table revision macros to fill DC `integrated_info`.
- AMDGPU power-management integration: `smu8_hwmgr.c` consumes `ATOM_INTEGRATED_SYSTEM_INFO_V1_9`; `ppatomctrl.c` consumes `ATOM_VRAM_INFO_HEADER_V2_2`, `ATOM_INIT_REG_BLOCK`, `GET_DATA_TABLE_*`, `ATOM_ASIC_PROFILING_INFO_V3_6`, and SMU/AVFS structures.
- DP integration: `amdgpu/atombios_dp.c` uses `PROCESS_AUX_CHANNEL_TRANSACTION_PARAMETERS_V2` and `PROCESS_AUX_CHANNEL_TRANSACTION_PS_ALLOCATION` with `amdgpu_atom_execute_table()`. Radeon has a parallel copy of these ABI definitions and call patterns.
- Firmware/ACPI integration: `UEFI_ACPI_VFCT`, `GOP_VBIOS_CONTENT`, and `GOP_LIB1_CONTENT` match AMD VFCT table layouts used to carry GOP/VBIOS images in system firmware.

## Risks and Edge Cases

- ABI packing is critical. The file uses `#pragma pack(1)` around BIOS data; any accidental padding, compiler-specific packing change, or type-width mismatch corrupts all offset-based parsing.
- Endianness-sensitive bitfields, especially `ATOM_TDP_CONFIG_BITS` and `ATOM_MEMORY_SETTING_ID_CONFIG`, depend on `ATOM_BIG_ENDIAN`. Bitfield layout is inherently compiler-sensitive, so consumers should prefer raw fields/masks when possible.
- Flexible arrays and placeholder arrays (`[]`, `[1]`, fixed arrays used "for allocation") make `sizeof` unsafe for table length validation. Callers must use firmware table header sizes, entry-size fields, offsets, and count fields.
- Table revisions are easy to mismatch. Many similarly named integrated-system-info, profiling, VRAM, and PowerPlay structures differ by a few fields but share prefixes; using the wrong content revision can shift every later field.
- Firmware data is untrusted input. Offsets such as `usExtDispConnInfoOffset`, VRAM patch offsets, DIG PHY offsets, VFCT image offsets, and table payload lengths need bounds checks before dereference.
- Unit mismatches are common: clocks may be 10 kHz, kHz, or Hz; voltages may be mV, 0.01 mV, 0.25 mV, or encoded fuse units; LVDS delays are 4 ms units; spread spectrum can be 0.01% or 0.001% depending on mode bits.
- BIOS scratch bits are shared across firmware and driver contexts. Incorrectly setting device-change, lid/dock, I2C, DPMS, or active-device bits can desynchronize display state or trigger wrong ACPI/display handling.
- Obsolete compatibility aliases can hide semantic drift. New code should prefer current names when possible, while maintaining compatibility for old VBIOS data.
- Several comments contain spelling mistakes or legacy notes; the comments are useful for ABI meaning but should not be treated as normative validation logic.

## Test Signals

- Build coverage: compile AMDGPU and Radeon paths that include this header, with attention to `-Wpacked`, bitfield, flexible-array, and duplicate-definition warnings.
- Firmware table parsing tests should exercise integrated-system-info revisions v1.7/v1.8/v1.9/v1.10, ASIC profiling v3.3-v3.6, VRAM info v2.1/v2.2, and display output info v2/v3 against representative VBIOS blobs.
- Runtime smoke tests: boot Carrizo/SMU8 and Polaris-class hardware or VBIOS fixtures and confirm integrated clocks, UMA clocks, display-clock voltage mappings, AVFS parameters, and VRAM module/timing tables parse without bounds errors.
- Display tests: DP AUX reads/writes through `ProcessAuxChannelTransaction`, DPCD link training, HPD ID routing, I2C DDC transactions, eDP voltage-swing mode selection, and LVDS backlight/power sequencing.
- Power tests: min/max VDDC derivation, AVFS parameter propagation, cTDP extraction, power-source sensor parsing, and spread-spectrum table selection for internal/external clock branches.
- Memory tests: VRAM module selection by external memory ID/GPIO strap, MC register patch block traversal, DRAM data remap parsing, MC microcode signature/length validation, and memory-type string reporting from MC scratch bits.
- Robustness tests: malformed VBIOS offsets/counts/revisions, truncated variable arrays, invalid `ucNumOfVRAMModule`, impossible DP AUX output lengths, unsupported integrated-info content revisions, and endian-config builds where feasible.
