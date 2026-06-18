# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios.h lines 5116-7980

## Scope

This chunk is the tail of the Radeon ATOM BIOS ABI header. It contains no executable C control flow of its own; instead it defines packed firmware table layouts, scratch-register bit contracts, command-table parameter blocks, version aliases, and legacy compatibility names consumed by the radeon ATOM parser, display, I2C/AUX, memory, and DPM code. The final `#pragma pack()` reset and `#include "pptable.h"` mean this file also controls ABI packing state for all earlier and later ATOM/PPLIB definitions.

## Purpose and Major Definitions

- `ATOM_INTEGRATED_SYSTEM_INFO_V1_8` describes Kaveri/Kabini APU platform data: boot SCLK/UMA/NB clocks, display voltage requirements, SBIOS/VBIOS capability flags, GPU reserved system memory, panel refresh range, memory type/channel count, TDP config, SCLK voltage tables, spread-spectrum defaults, LVDS sequencing, NB P-state clocks/voltages, and embedded external display connector info. `ATOM_FUSION_SYSTEM_INFO_V2` wraps this table with a 128-dword PowerPlay payload.
- External I2C setup and spread-spectrum tables are defined by `ATOM_I2C_DATA_RECORD`, `ATOM_I2C_DEVICE_SETUP_INFO`, `ATOM_ASIC_MVDD_INFO`, `ATOM_ASIC_SS_ASSIGNMENT`, `_V2`, `_V3`, and `ATOM_ASIC_INTERNAL_SS_INFO` variants. These describe clock branches such as memory, engine, UVD, TMDS, HDMI, LVDS, DP, DCPLL, VCE, and GPUPLL, with target clock ranges, percentage units, modulation rates, center/down/external mode bits, and optional 0.001 percent encoding in v3.
- BIOS scratch register masks cover scratch slots 0-9: connected devices, ROM location, TV standard/backlight/DPMS/rotation, active devices and CRTCs, LCD panel/refresh/VRAM info, DOS requested devices, ACPI display requests and state-change flags, DOS mode state, and I2C busy/completed/aborted state. The same concepts are exposed as 32-bit masks, byte masks, shifts, and encoded set/clear command constants.
- Driver macros `GetIndexIntoMasterTable`, `GET_COMMAND_TABLE_COMMANDSET_REVISION`, `GET_COMMAND_TABLE_PARAMETER_REVISION`, `GET_DATA_TABLE_MAJOR_REVISION`, and `GET_DATA_TABLE_MINOR_REVISION` translate C table-field names and common table headers into ATOM parser indices and revisions.
- VBIOS-only command parameter blocks include memory PLL init, GPIO pin access, scaler enable, hardware cursor/icon, graphics surface setup versions, memory cleanup, display surface size, palette data operations, interrupt services, indirect IO access, OEM info, TV/VESA timing maps, memory initialization register blocks, memory timing formats, VRAM module descriptors, software I2C parameters, VESA/VBE information blocks, BIOS interrupt function/subfunction constants, display-output/transmitter/encoder tables, AUX/DP/I2C transaction parameters, hardware miscellaneous operations, hardware block instance selection, DIG transmitter analog/PHY condition tables, graphics harvesting parameters, MC scratch memory-type values, legacy DAC/TMDS/connector tables, legacy PowerPlay tables, compatibility aliases, DPMS aliases, and AMD ACPI VFCT/GOP image structures.

## Important APIs, Types, and Integration Points

- `kv_dpm.c` consumes `ATOM_INTEGRATED_SYSTEM_INFO_V1_8` directly through a union, requires content revision 8, and maps fields into `kv_power_info`: boot clocks, HTC limits, NB DPM enable from `ulSystemConfig` bit 3, NB P-state clocks, DFS bypass, and SCLK/VID mapping tables.
- `radeon_atombios.c` consumes `ATOM_VRAM_INFO_V3`, `ATOM_VRAM_INFO_V4`, and `ATOM_VRAM_INFO_HEADER_V2_1` in `radeon_atom_get_memory_info()`. It walks variable-sized module records using `usSize` or `usModuleSize`, then extracts memory vendor and type.
- `atombios_dp.c` uses `PROCESS_AUX_CHANNEL_TRANSACTION_PARAMETERS`/`_V2` through scratch memory for DP AUX and `DP_ENCODER_SERVICE_PARAMETERS` for sink-type and training-related commands.
- `atombios_i2c.c` uses `PROCESS_I2C_CHANNEL_TRANSACTION_PARAMETERS` for ATOM-mediated hardware I2C, while `radeon_i2c.c` sets and clears `ATOM_S6_HW_I2C_BUSY_STATE` in `RADEON_BIOS_6_SCRATCH` around lower-level I2C transactions.
- `atombios_encoders.c` reads/writes `ATOM_S2_CURRENT_BL_LEVEL_MASK` and `ATOM_S2_CURRENT_BL_LEVEL_SHIFT` for backlight state, and many encoder/CRTC paths use `GetIndexIntoMasterTable(COMMAND, ...)` aliases defined here.
- DPM implementations across r600/rv6xx/rv770/rs780/sumo/trinity/ni/si/ci/kv use `GetIndexIntoMasterTable(DATA, PowerPlayInfo)` and the legacy `ATOM_POWERPLAY_INFO`/`_V2`/`_V3` compatibility layouts before newer PPLIB structures.

## Control Flow and State Behavior

This header encodes firmware data flow rather than local functions. Runtime flow usually follows this pattern:

1. The driver parses the ATOM master table with `GetIndexIntoMasterTable(DATA, ...)` or `GetIndexIntoMasterTable(COMMAND, ...)`.
2. It verifies the table header format/content revision using ATOM parser helpers or the macros here.
3. It overlays one of these packed structs on the BIOS image or populates a command-parameter struct.
4. It converts little-endian fields with `le16_to_cpu`/`le32_to_cpu` at call sites and executes command tables through `atom_execute_table()` or scratch-backed variants.
5. Firmware-visible state is persisted in GPU BIOS scratch registers and in the BIOS image tables. Driver-side derived state is cached in subsystem structs such as `kv_power_info`, `atom_memory_info`, connector state, and radeon I2C channel state.

The scratch definitions are especially stateful. `ATOM_S2_*` stores backlight, DPMS, forced low-power mode, VariBright, and rotation. `ATOM_S3_*` mirrors active devices and CRTC ownership. `ATOM_S6_*` communicates ACPI/device changes, lid/dock/critical/thermal events, I2C busy state, display reconfiguration, and requested devices. Since these bits are shared with firmware/ACPI paths, updates must be read-modify-write and synchronized by the relevant driver locks.

## Dependencies and ABI Constraints

- Depends on earlier `atombios.h` definitions such as `ATOM_COMMON_TABLE_HEADER`, `ATOM_CLK_VOLT_CAPABILITY`, `ATOM_TDP_CONFIG`, `ATOM_AVAILABLE_SCLK_LIST`, `ATOM_EXTERNAL_DISPLAY_CONNECTION_INFO`, `ATOM_I2C_ID_CONFIG_ACCESS`, object/device IDs, command table names, and PPLIB aliases.
- Depends on `pptable.h` after the include guard for PowerPlay/PPLIB structures referenced by DPM unions in source files.
- Uses flexible arrays and allocation-sized placeholder arrays (`[]`, `[1]`, fixed maximum arrays) because firmware records are variable length. Call sites must use table size, count, and per-record size fields rather than `sizeof` alone.
- Endianness is part of the ABI. Some bitfield structs have `#if ATOM_BIG_ENDIAN`, but most consumers must explicitly convert little-endian BIOS fields.
- Packing is critical. The chunk ends with `#pragma pack()` and defines VFCT with `#pragma pack(1)`; changing packing around these structs would corrupt firmware offsets.

## Risks and Edge Cases

- ABI drift is the primary risk. Reordering, resizing, or changing field types in these structs can break BIOS table parsing, command execution, memory detection, display bring-up, or DPM behavior across old ASIC families.
- Variable-length records can be malformed by bad firmware. `radeon_atom_get_memory_info()` guards zero module size, but every walker of `asI2CData[]`, `asSpreadSpectrum[]`, `ATOM_INIT_REG_BLOCK`, VRAM modules, PHY condition lists, and VBE/TV mode tables needs bounds from the parsed table header.
- Scratch-register bit definitions are shared state. Lost updates or stale bits can misreport active devices, block display switching, leave I2C marked busy, corrupt backlight level, or confuse ACPI event handling.
- Several aliases intentionally map old names onto newer tables and commands (`Object_Info`, `VRAM_GPIO_DetectionInfo`, `DispOutInfo`, `DFP*`, `TMDS*`, `EnableLVDS_SS`). Removing or changing them can break older code paths even when the canonical table still exists.
- Comments document many platform-specific defaults and zero-as-default semantics, especially LVDS sequencing, spread-spectrum, panel refresh, PWM backlight, HTC limits, and NB clocks. Consumers must preserve fallback behavior when fields are zero.
- Some definitions are marked obsolete or VBIOS-only but remain included in the kernel build. They should be treated as compatibility ABI, not dead code.

## Test Signals

- Build signal: compile the radeon driver with this header included by ATOM parser, display, I2C, DP, and DPM sources; any struct or alias breakage should surface as compile errors across these consumers.
- Firmware parsing signal: boot or test with ATOM BIOS images spanning VRAM table revisions 1.3, 1.4, and 2.1; verify `radeon_atom_get_memory_info()` reports the expected memory type/vendor and does not overrun malformed module sizes.
- Kaveri/Kabini DPM signal: exercise `kv_parse_sys_info_table()` with content revision 8 and validate boot clocks, HTC defaults, NB P-state clocks, DFS bypass, and SCLK/VID mapping.
- Display state signal: change backlight, DPMS, lid/dock/display configuration, and connector hotplug state while checking BIOS scratch registers 2, 3, and 6 for expected masks.
- DP/AUX/I2C signal: run DP AUX DPCD reads, sink-type queries, and hardware I2C transfers; confirm command-table argument packing, scratch buffer offsets, reply statuses, and busy-bit cleanup.
- Spread-spectrum/PHY signal: parse `ASIC_InternalSS_Info` and DIG transmitter info tables on boards with DP/HDMI/LVDS spread-spectrum requirements; validate percentage unit handling and center/external mode bits.

## Chunk Notes for Merge Lane

This is the final chunk of `sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atombios.h`. The merged per-file report should combine this ABI/compatibility material with earlier chunks covering master table definitions, command parameter blocks, object tables, firmware info, voltage tables, and PPLIB structures.
