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

Important data-table families include firmware info `v3_1` through `v3_5`; LCD, GPIO, display object, connector, HPD, AUX/DDC, and external display records; DCE/DCN controller info `v4_1` through `v4_5`; integrated system info `v1_11` through `v2_3`; GFX, SMU, SMC DPM, UMC, VRAM, voltage object, and ASIC profiling structures. Important command families include ASIC init, engine/memory/pixel/DCE clocks, voltage control, efuse reads, SMU clock queries, dynamic memory settings, memory training, CRTC control, I2C/AUX transactions, DIG encoder/transmitter control, and external encoder control.

The header ends by including `atomfirmwareid.h`, which binds compact data/command table IDs to this ABI.

## Control Flow

There is no control flow inside this header. Runtime flow is implemented by consumers that use these layouts:

- ATOM parser setup reads the ROM header pointer, casts the ROM header, follows `masterdatatable_offset` or `masterhwfunction_offset`, and then indexes one of the master lists to locate a target table/function.
- AMDGPU ATOM firmware helpers read a table header, branch on `format_revision` and `content_revision`, and cast to a matching versioned structure such as `atom_firmware_info_v3_1`, `v3_3`, `v3_4`, or `v3_5`.
- Power-management code loads SMC DPM info tables, copies version-specific board parameters into SMU powerplay tables, and uses firmware-info fields for boot frequencies, firmware reservations, PSP bootloader checks, and platform limits.
- Display code parses display object and integrated system info records to build connector, HPD, AUX/DDC, panel, retimer, eDP, and PHY-tuning state.
- Command-table callers fill one of the command parameter structures, invoke the ATOM BIOS parser for the relevant command-table offset, then read back output fields or status unions such as I2C/AUX transaction status.

## State and Persistence Behavior

The header has no runtime state of its own. It describes persistent and semi-persistent firmware-owned data. VBIOS image bytes persist in ROM or copied BIOS memory. `vram_usagebyfirmware_v2_1` and `v2_2` describe reserved framebuffer regions and document posted/unposted VBIOS, generation, and SR-IOV reservation behavior. Scratch-register definitions map firmware/driver communication bits for display, backlight, lid/AC, pre-OS mode, and ASIC-init state. Command parameter structures are transient call frames, but command execution can change durable hardware state such as clocks, voltage, memory training, display power, encoders, I2C devices, and AUX targets.

## Dependencies

The file depends on fixed-width integer types being available, except when `_H2INC` is used to provide simple typedefs for header-to-include conversion. It depends on packed-structure compiler behavior and includes `atomfirmwareid.h` at the end by design. Some variable-length payloads rely on C flexible arrays or kernel annotations such as `__counted_by`.

Consumers depend on AMDGPU ATOM parser helpers, `amdgpu_atomfirmware.c`, `amdgpu_atomfirmware.h`, Display Core, PowerPlay/SMU code, VBIOS ROM access, and firmware-specific generated register headers. External correctness depends on VBIOS producer tools preserving these exact layouts and revisions.

## Integration Points

Representative includes and consumers include `amdgpu/atom.c`, `amdgpu/amdgpu_atomfirmware.c`, `display/dmub/inc/dmub_cmd.h`, PowerPlay hwmgr files, and SW SMU code for SMU11 through SMU15. Call sites cast firmware bytes to `atom_firmware_info_v3_*`, `atom_smc_dpm_info_v4_*`, and display/VRAM/UMC tables. Beige Goby-specific SMU code uses `atom_smc_dpm_info_v4_9` fields to populate `PPTable_beige_goby_t`.

## Risks and Edge Cases

- This file is a binary ABI. Reordering, resizing, changing signedness, removing reserved fields, or dropping `#pragma pack(1)` breaks VBIOS parsing.
- Version handling is mandatory. A field present in one table revision cannot be read from another revision unless the layout guarantees it.
- Tables contain offsets to nested blocks and variable-length arrays. Consumers must bounds-check against `structuresize` and the BIOS image before casting or iterating.
- Units vary across fields: 10 kHz, 100 Hz, 10 Hz, millivolts, milliwatts, KB, 16 MB chunks, Q formats, and 4 ms panel delays.
- VRAM reservation rules differ by VBIOS posted state, generation, and SR-IOV role; mistakes can corrupt firmware-reserved framebuffer memory.
- Command structures use unions and in/out fields. Using the wrong command revision can mask hardware failures.

## Test Signals

Compile coverage of AMDGPU, Display Core, PowerPlay, and SMU generations catches missing type/field names. VBIOS parsing tests should exercise revision dispatch, `structuresize` bounds, master table offsets, and variable-length table walking. Boot tests should validate firmware-info boot clocks, reserved memory, VRAM/UMC data, and SMU DPM ingestion. Display tests validate connector/HPD/AUX/eDP/PHY data. Power-management tests should compare decoded telemetry, I2C controller settings, VR mapping, spread spectrum, and boot clocks against known-good VBIOS/SMU traces.
