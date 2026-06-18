# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmwareid.h

## Purpose

`atomfirmwareid.h` defines compact enum IDs for ATOM VBIOS master data tables and command tables. It is the ID companion to `atomfirmware.h`: `atomfirmware.h` defines the table directory layout and payload structures, while this file assigns stable symbolic IDs that helper code can use when asking for a specific VBIOS table or command by logical name.

## Important APIs, Types, and Macros

The header exports two enums and no functions or storage:

- `enum atom_master_data_table_id` enumerates data-table IDs: utility pipeline, multimedia info, firmware info, LCD info, SMU info, VRAM usage by firmware, GPIO pin LUT, GFX info, powerplay info, display object info, indirect IO access, UMC info, DCE info, VRAM info, integrated system info, ASIC profiling info, voltage object info, and `VBIOS_DATA_TBL_ID__UNDEFINED`.
- `enum atom_master_command_table_id` enumerates command IDs: ASIC init, DIG encoder control, engine/memory/pixel/DCE clocks, display power gating, CRTC blank/enable/source/timing, external encoder, I2C transaction, GPU clock computation, dynamic memory settings, memory training, set voltage, DIG1 transmitter control, AUX transaction, get voltage info, and `VBIOS_CMD_TBL_ID__UNDEFINED`.

The order is significant: IDs are dense enum values used to map logical IDs onto offsets in the master lists defined in `atomfirmware.h`.

## Control Flow

There is no internal control flow. Consumers use these IDs as switch or index inputs. A data-table helper maps a `VBIOS_DATA_TBL_ID__*` value to the corresponding field in `struct atom_master_list_of_data_tables_v2_1`. A command helper maps a `VBIOS_CMD_TBL_ID__*` value to `struct atom_master_list_of_command_functions_v2_1`, fills the appropriate command parameter structure from `atomfirmware.h`, and invokes the ATOM parser. Undefined IDs provide sentinels for failed lookup or unsupported requests.

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

Build tests catch missing enum names used by firmware helper code. Unit-style tests for ATOM table lookup should verify each data/command ID resolves to the intended master-list field. Negative tests should ensure `*_UNDEFINED` and out-of-range IDs fail cleanly. VBIOS integration tests should pair ID lookup with revision/size validation of the resulting table.
