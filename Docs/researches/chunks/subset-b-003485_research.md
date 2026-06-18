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
