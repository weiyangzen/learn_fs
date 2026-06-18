# subset-b-003517 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_overdriver.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_overdriver.c

### Purpose
`pp_overdriver.c` is a data-backed helper for Vega10 overdrive/AVFS defaults. Almost the whole file is `vega10_fuses_default[]`, a static table of 1,235 keyed default fuse records plus a zero-key sentinel. The single exported function, `pp_override_get_default_fuse_value()`, lets higher-level Vega10 power management recover fallback VFT coefficients when a board/serial key is recognized.

### Important APIs, types, and data
The file includes `pp_overdriver.h` and `<linux/errno.h>`. Its only file-local data structure is `static const struct phm_fuses_default vega10_fuses_default[]`, whose entries carry a 64-bit `key` and VFT2/VFT1/VFT0 triplets (`m1`, `m2`, `b`). The exported API is:

- `int pp_override_get_default_fuse_value(uint64_t key, struct phm_fuses_default *result)`: scans the table until the sentinel, copies the matched record to `result`, and returns `0`; returns `-EINVAL` when no key matches.

### Control flow
The lookup path is intentionally simple. It assigns `list = vega10_fuses_default`, iterates `for (i = 0; list[i].key != 0; i++)`, compares the caller's key, field-copies the matching table entry, and exits. If the loop reaches the sentinel, it returns `-EINVAL`. There is no sorting, hashing, caching, or platform detection in this file.

### State and persistence behavior
All persisted state is compile-time constant data in the driver image. The function does not allocate memory, mutate global state, talk to hardware, or retain references. The caller-owned `result` buffer is overwritten only on success. Failed lookup leaves `result` untouched.

### Dependencies and integration points
`vega10_hwmgr.c` calls this helper when deriving AVFS/fuse values from a board serial number. The helper depends on the struct contract in `pp_overdriver.h` and on kernel `-EINVAL`. Its correctness depends on the external key source matching the table's 64-bit keys and on callers passing a valid non-NULL `result` pointer.

### Risks and edge cases
There is no NULL check for `result`; a matched key with a NULL result pointer would dereference NULL. Lookup is linear over a large static table, which is acceptable for infrequent initialization but not suitable for hot paths. Duplicate keys would silently prefer the first entry. Unknown boards receive `-EINVAL`, so callers must have a fallback path. The table is opaque calibration data, so accidental reordering is low risk but value corruption is hard to detect by code review alone.

### Test signals
Useful tests would exercise a known first entry, a known late entry, the zero-key miss path, and an unknown key returning `-EINVAL`. Integration signals are Vega10 initialization logs and AVFS behavior in `vega10_hwmgr.c`, especially whether default fuse overrides are applied only when the serial/key matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_overdriver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_overdriver.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_overdriver.h

### Purpose
`pp_overdriver.h` declares the tiny public interface for Vega overdrive default fuse lookup. It defines the record shape consumed by `pp_overdriver.c` and exported to ASIC-specific hwmgr code.

### Important APIs and types
The main type is `struct phm_fuses_default`, with a 64-bit lookup `key` and three voltage/frequency transfer coefficient groups: `VFT2_m1/m2/b`, `VFT1_m1/m2/b`, and `VFT0_m1/m2/b`. The only function prototype is `pp_override_get_default_fuse_value(uint64_t key, struct phm_fuses_default *result)`.

### Control flow and state
This header has no executable code and no persistent state. It carries include guards, includes Linux integer/kernel definitions, and exposes the struct/function contract used by `pp_overdriver.c`.

### Dependencies and integration points
Consumers include this header when they need fallback fuse coefficients, notably Vega10 power management. The header depends only on standard kernel integer definitions and does not pull in hwmgr state, which keeps it isolated from broader powerplay internals.

### Risks and test signals
The ABI risk is field ordering: callers expect exact names and sizes when copying table records. Because the implementation does field-by-field copies rather than struct assignment, adding fields would require updating `pp_override_get_default_fuse_value()`. Build coverage should catch prototype mismatches; functional coverage needs the `.c` lookup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_overdriver.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_psm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_psm.c

### Purpose
`pp_psm.c` implements the legacy Power State Manager glue for `struct pp_hwmgr`. It builds an in-memory table of BIOS/PPTable power states, tracks requested/current/boot/UVD states, selects boot/performance/user states by classification labels, and applies dynamic power-state changes through the common PHM hooks.

### Important APIs and functions
Exported functions match `pp_psm.h`:

- `psm_init_power_state_table()`: queries ASIC hwmgr callbacks for table count and per-state private size, allocates `hwmgr->ps`, `request_ps`, and `current_ps`, fills entries via `get_pp_table_entry()`, assigns one-based IDs, and records boot/UVD pointers.
- `psm_fini_power_state_table()`: frees allocated power-state buffers and clears pointers.
- `psm_set_boot_states()` / `psm_set_performance_states()`: find a state by `PP_StateClassificationFlag_Boot` or `PP_StateUILabel_Performance` and copy it into `hwmgr->request_ps`.
- `psm_set_user_performance_state()`: returns a pointer to a state matching a UI label, falling back from Battery/Balanced to Performance.
- `psm_adjust_power_state_dynamic()`: applies display changes, state transition rules, forced DPM level changes, and workload/power-profile updates.

File-local helpers include `psm_get_ui_state()`, `psm_get_state_by_classification()`, `psm_set_states()`, and `power_state_management()`.

### Control flow
Initialization is callback-driven. If `get_num_of_pp_table_entries` or `get_power_state_size` is missing, initialization returns success with no PSM table. If table count or state size is invalid, it warns, zeros `num_ps`/`ps_size`, and returns success so newer ASICs without this PSM can continue. Otherwise it allocates a contiguous state arena where each record is `sizeof(struct pp_power_state) + ASIC-private-size`; pointer arithmetic advances by `hwmgr->ps_size`.

Dynamic adjustment first gates display/state handling behind `hwmgr->not_vf`. When PSM state exists, `power_state_management()` picks either the explicit `new_ps` or `request_ps`, calls `phm_apply_state_adjust_rules()`, compares current and requested hardware states with `phm_check_states_equal()`, and calls `phm_set_power_state()` when hardware differs or display configuration requires SMC update. Without a PSM table, it still runs `phm_apply_clock_adjust_rules()` so DAL clock limits can be honored on ASICs such as Vega12/Vega20.

After state handling, `psm_adjust_power_state_dynamic()` applies requested forced DPM level with `phm_force_dpm_levels()` and updates `hwmgr->dpm_level` on success. Unless in manual DPM mode, it chooses the highest set workload bit via `fls(hwmgr->workload_mask)`, maps it through `hwmgr->workload_setting`, and calls `set_power_profile_mode()` if the profile changed and the ASIC supplies that callback.

### State and persistence behavior
The module owns heap-backed `hwmgr->ps`, `request_ps`, and `current_ps`; `boot_ps` and `uvd_ps` are pointers into the `ps` arena. Requested and current states are full copies, not borrowed pointers. `psm_set_states()` mutates only `request_ps`. `power_state_management()` mutates hardware via PHM hooks and then copies `request_ps` to `current_ps`. The DPM/workload section mutates `hwmgr->dpm_level` and may update firmware-visible power profile state.

### Dependencies and integration points
This file depends on `hwmgr->hwmgr_func` callbacks, PHM helpers (`phm_apply_state_adjust_rules`, `phm_check_states_equal`, `phm_set_power_state`, display notification helpers, DPM/profile helpers), kernel allocation (`kcalloc`, `kzalloc`, `kfree`), and classification/label enums from hwmgr headers. `hwmgr.c` calls these functions during hwmgr init, start, suspend/resume, performance-level changes, and user profile changes.

### Risks and edge cases
The code treats missing PSM support as successful initialization, so callers must distinguish `hwmgr->ps == NULL` from a fatal error. Several public functions return `0` when `hwmgr->ps` is absent, which can hide unsupported state transitions. `power_state_management()` passes `&pcurrent->hardware` to `phm_set_power_state()` even after `pcurrent == NULL` would make `equal = false`; in normal initialized paths `current_ps` exists, but direct misuse would be unsafe. User-state fallback changes Battery/Balanced requests to Performance, which is intentional but important for UI semantics. Workload selection uses the highest set workload bit, so masks with multiple bits collapse to one profile.

### Test signals
Unit-level signals include allocation failure cleanup, missing callback/no-table behavior, boot/performance classification lookup, Battery/Balanced fallback, and invalid labels returning `-EINVAL`. Integration signals are successful hwmgr initialization (`psm_init_power_state_table()` from `hwmgr.c`), display-change transitions invoking SMC notification, forced manual DPM mode not changing power profiles, and ASICs without PSM still applying DAL clock-adjust rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_psm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_psm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_psm.h

### Purpose
`pp_psm.h` exposes the legacy Power State Manager lifecycle and state-selection API to hwmgr orchestration code. It is the narrow public contract for initializing, selecting, adjusting, and freeing PSM state.

### Important APIs
The header declares `psm_init_power_state_table()`, `psm_fini_power_state_table()`, `psm_set_boot_states()`, `psm_set_performance_states()`, `psm_set_user_performance_state()`, and `psm_adjust_power_state_dynamic()`. The user-state function returns a `struct pp_power_state **` selected from the internal table. The dynamic adjust function accepts `skip_display_settings` and an optional explicit `new_ps` override.

### Control flow and state
There is no executable code in the header. It includes `hwmgr.h`, so it intentionally exposes hwmgr-owned state types and enums. The declared functions mutate `struct pp_hwmgr` fields and, through the `.c` implementation, may program hardware/SMC state.

### Dependencies and integration points
Primary callers are in `hwmgr.c`, which sequences PSM initialization during hardware manager setup and calls boot/performance/user state transitions around start, suspend, resume, and profile changes. ASIC-specific hwmgr callbacks fill the table that this API manages.

### Risks and test signals
The interface communicates support absence through successful calls with `hwmgr->ps == NULL`, so callers should not assume every `0` return means a state was selected or applied. Build coverage should catch type/prototype drift with `hwmgr.c`; runtime tests should validate that user state pointers are not retained after `psm_fini_power_state_table()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/pp_psm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.c

### Purpose
`ppatomctrl.c` is the legacy ATOM BIOS control adapter for AMD PowerPlay hwmgr code. It converts ATOM data-table and command-table formats into normalized hwmgr structures for memory-controller timing, PLL divider calculation, voltage/GPIO control, spread spectrum, eFuse/leakage values, AVFS parameters, SMC clock ranges, and voltage rails.

### Important APIs and functions
The file exports many helpers declared in `ppatomctrl.h`:

- MC timing: `atomctrl_initialize_mc_reg_table()`, `atomctrl_initialize_mc_reg_table_v2_2()`, `atomctrl_set_engine_dram_timings_rv770()`, `atomctrl_set_ac_timing_ai()`.
- PLL/clock: `atomctrl_get_memory_pll_dividers_si/vi/ai()`, `atomctrl_get_engine_pll_dividers_kong/vi/ai()`, `atomctrl_get_dfs_pll_dividers_vi()`, `atomctrl_get_reference_clock()`, `atomctrl_get_mpll_reference_clock()`.
- Voltage/GPIO: `atomctrl_is_voltage_controlled_by_gpio_v3()`, `atomctrl_get_voltage_table_v3()`, `atomctrl_get_pp_assign_pin()`, `atomctrl_get_voltage_evv_on_sclk()`, `atomctrl_get_voltage_evv()`, `atomctrl_get_voltage_evv_on_sclk_ai()`, `atomctrl_get_svi2_info()`, `atomctrl_get_voltage_range()`, `atomctrl_get_vddc_shared_railinfo()`.
- Spread spectrum and fuses: `atomctrl_is_asic_internal_ss_supported()`, `atomctrl_get_memory_clock_spread_spectrum()`, `atomctrl_get_engine_clock_spread_spectrum()`, `atomctrl_read_efuse()`.
- Profiling/leakage: `atomctrl_get_avfs_information()`, `atomctrl_get_leakage_id_from_efuse()`, `atomctrl_get_leakage_vddc_base_on_leakage()`, `atomctrl_get_edc_hilo_leakage_offset_table()`, `atomctrl_get_edc_leakage_table()`.

Private helpers parse variable-sized BIOS structures: `atomctrl_retrieve_ac_timing()`, `atomctrl_set_mc_reg_address_table()`, `get_voltage_info_table()`, `atomctrl_lookup_voltage_type_v3()`, `atomctrl_lookup_gpio_pin()`, `get_gpio_lookup_table()`, `asic_internal_ss_get_ss_table()`, `asic_internal_ss_get_ss_asignment()`, and EDC table access helpers.

### Control flow
Most functions follow one of two patterns. Data-table readers call `smu_atom_get_data_table(hwmgr->adev, GetIndexIntoMasterTable(DATA, ...), ...)`, validate revision/size enough for the expected struct, then copy little-endian BIOS fields into native hwmgr structs. Command-table helpers prepare a packed ATOM parameter struct, call `amdgpu_atom_execute_table(..., GetIndexIntoMasterTable(COMMAND, ...), ...)`, and decode the same buffer as the output struct on success.

MC register initialization reads `VRAM_Info`, finds the memory clock patch table, extracts register addresses until the placeholder/end bit, then walks timing data blocks matching the requested VRAM module ID. PLL helpers use `ComputeMemoryClockParam` or `ComputeMemoryEnginePLL` command revisions and return ASIC-specific divider structs. Voltage helpers find a matching voltage object by walking variable-sized voltage objects within `VoltageObjectInfo`; GPIO modes build voltage tables, while EVV paths call `GetVoltageInfo`.

Spread-spectrum selection walks `ASIC_InternalSS_Info` assignments and chooses the first clock-source entry whose target range covers the requested clock, with revision-dependent rate scaling. AVFS and leakage functions read ASIC profiling/GFX info tables and map revision-specific fields into simpler structures.

### State and persistence behavior
The file itself stores no persistent mutable state. It mutates caller-provided output buffers and sometimes writes through pointers such as `*voltage`, `*efuse`, `*shared_rail`, `*max_vddc`, and `*min_vddc`. Several command-table calls can program or query firmware/BIOS state, especially dynamic memory settings and voltage/efuse commands. All BIOS table pointers are borrowed from ATOM/SMU table accessors and are not retained by this file.

### Dependencies and integration points
This file depends on `atom.h`, `atombios.h`, `cgs_common.h`, `pp_debug.h`, kernel delay/allocation headers, `smu_atom_get_data_table()`, `amdgpu_atom_execute_table()`, `le16_to_cpu`/`le32_to_cpu`, ATOM table revision structs, and hwmgr dynamic state. It is used by SMU7/Fiji-era hwmgr code for voltage tables and leakage handling, by memory/clock setup code for PLL divider calculations, and by ASIC-specific paths that need ATOM BIOS-derived AVFS or SMC range data.

### Risks and edge cases
The code parses variable-length firmware tables with pointer arithmetic, so malformed table sizes, missing sentinels, or too many entries are high-risk inputs. Some paths assert table presence and return errors, while others assume a lookup succeeded; for example `atomctrl_get_svi2_info()` dereferences `voltage_object` after lookup without a NULL check. `atomctrl_get_smc_sclk_range_table()` copies `ucSclkEntryNum` entries without checking against `MAX_SCLK_RANGE`. `atomctrl_read_efuse()` has mask logic that assumes sane `start_index <= end_index` and lengths no larger than 32. `get_edc_leakage_table()` computes `table_address += offset` but returns `temp`, so the offset does not affect the returned pointer; that looks suspicious for callers expecting an offset GFX subtable. Many functions return `-1` instead of a specific errno, so callers often need to treat any nonzero as failure.

### Test signals
Good validation needs firmware-table fixtures for each supported revision and command-table mocks that verify parameter packing. Targeted tests should cover invalid/missing `VRAM_Info`, voltage object lookup misses, too many GPIO voltage entries, spread-spectrum table revision scaling, eFuse boundary masks, leakage-bin mapping, and `MAX_SCLK_RANGE` overflow behavior. Integration signals include SMU7/Fiji voltage table setup, memory clock divider programming, dynamic memory timing changes, and boot on boards with missing optional BIOS tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.h

### Purpose
`ppatomctrl.h` is the public type and function contract for the legacy ATOM BIOS PowerPlay adapter. It defines normalized hwmgr-facing structures that hide the raw ATOM table layouts used in `ppatomctrl.c`.

### Important APIs and types
The header defines clock divider structures for older ASIC families (`pp_atomctrl_clock_dividers`, `_rv730`, `_kong`, `_ci`, `_vi`, `_ai`), memory PLL structures (`pp_atomctrl_memory_clock_param`, `_ai`), spread-spectrum structures/enums, voltage tables, MC register/timing tables, GPIO pin assignment, AVFS parameters, SCLK range tables, and EDC leakage table shapes. Constants such as `PP_ATOMCTRL_MAX_VOLTAGE_ENTRIES`, `VBIOS_MC_REGISTER_ARRAY_SIZE`, `VBIOS_MAX_AC_TIMING_ENTRIES`, and `MAX_SCLK_RANGE` bound fixed-size output arrays.

Function declarations cover BIOS GPIO/voltage lookups, EVV voltage calculation, reference clocks, spread spectrum, MC timing table initialization, DRAM timing programming, memory/engine PLL divider calculation, eFuse reads, AVFS/profiling reads, leakage table reads, and shared rail lookup.

### Control flow and state
There is no executable code. The header establishes caller-owned output buffer contracts. The `.c` implementation fills these buffers from ATOM data/command tables and usually returns `0` on success with nonzero/negative values on failure.

### Dependencies and integration points
The header includes `hwmgr.h`, so it is part of the internal AMDGPU powerplay hwmgr interface rather than a generic BIOS parser. ASIC-specific hwmgr implementations include it to acquire voltage tables, PLL dividers, AVFS data, and memory timings from legacy ATOM BIOS.

### Risks and test signals
Fixed-size arrays must stay aligned with implementation bounds. If firmware exposes more voltage entries, MC registers, timing entries, or SCLK ranges than the constants allow, the implementation must reject or clamp safely. Several exported structs mirror hardware/firmware units such as 10 kHz clocks, millivolts, 0.25 mV units, GPIO masks, and FCW fields; tests should verify unit conversions at the `.c` boundary. Build tests catch prototype drift, while table-fixture tests catch layout/revision mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomfwctrl.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomfwctrl.c

### Purpose
`ppatomfwctrl.c` is the atomfirmware-era counterpart to `ppatomctrl.c`, used by Vega/SOC15-style power management. It reads atomfirmware v2.1 master data/command tables, normalizes voltage object v4, clock, AVFS, GPIO, boot, and SMC DPM information, and exposes those values to ASIC hwmgr code.

### Important APIs and functions
The exported APIs are:

- `pp_atomfwctrl_is_voltage_controlled_by_gpio_v4()` and `pp_atomfwctrl_get_voltage_table_v4()`: inspect voltage object v4 entries for GPIO LUT or SVID2 voltage control data.
- `pp_atomfwctrl_get_gpu_pll_dividers_vega10()`: executes `computegpuclockparam` and returns SOC15 clock/divider/spread-spectrum fields.
- `pp_atomfwctrl_get_avfs_information()`: reads `asic_profiling_info` revisions 4.1 and 4.2 into `pp_atomfwctrl_avfs_parameters`.
- `pp_atomfwctrl_get_gpio_information()`: reads AC/DC, VR-hot, and firmware CTF GPIO metadata from `smu_info`.
- `pp_atomfwctrl_get_clk_information_by_clkid()`: executes `getsmuclockinfo` and returns a 10 kHz frequency.
- `pp_atomfwctrl_get_vbios_bootup_values()`: reads firmware info revision 3.1 or 3.2 and augments boot clocks with SMU clock-info command queries.
- `pp_atomfwctrl_get_smc_dpm_information()`: copies SMC DPM I2C, VR, telemetry, GPIO, LED, spread-spectrum, and mapping fields.

Private helpers include `pp_atomfwctrl_lookup_voltage_type_v4()`, `pp_atomfwctrl_get_voltage_info_table()`, and the firmware-info copy helpers for v3.1 and v3.2.

### Control flow
Voltage table functions fetch `voltageobject_info`, walk variable-size `union atom_voltage_object_v4` entries by `object_size`, and either copy GPIO LUT entries or SVID2 control metadata. PLL and clock functions execute atomfirmware command-table entries selected through `GetIndexIntoMasterCmdTable()`, then decode the output overlay from the same parameter buffer.

AVFS parsing fetches `asic_profiling_info`, checks common header `format_revision`/`content_revision`, handles revision 4.1 with ACG fields zeroed, and handles 4.2 with the added ACG GB tables. Boot-value parsing fetches `firmwareinfo`; revision 3.1 uses SMU9 clock IDs and revision 3.2 uses SMU11 clock IDs, with optional clock queries left as zero if the command fails.

### State and persistence behavior
The file has no global mutable state. It mutates caller-provided output structs. Command-table calls query firmware-calculated values but this file does not retain firmware table pointers. Some output fields are explicitly zero-initialized on older table revisions, but most functions assume the caller supplied a clean or fully overwritten buffer.

### Dependencies and integration points
It depends on `ppatomfwctrl.h`, `atomfirmware.h`, `atom.h`, `pp_debug.h`, `smu_atom_get_data_table()`, `amdgpu_atom_execute_table()`, atomfirmware v2.1 master table index macros, and endian conversion helpers. Vega10 hwmgr uses AVFS information and fuse-related coefficients; Vega12 process PPTable code uses SMC DPM information; SOC15 clock setup uses the PLL divider and SMU clock-info helpers.

### Risks and edge cases
Variable-sized voltage object walking depends on nonzero, valid `object_size`; malformed firmware could cause bad iteration. `pp_atomfwctrl_get_voltage_table_v4()` limits GPIO LUT count but SVID2 mode fills only metadata and leaves `count` at zero, so callers must branch on voltage mode. AVFS revision handling rejects unknown revisions, which is safer than misparsing but can block newer firmware unless code is updated. In the v4.2 AVFS branch, `ulPhyclk2GfxclkM1` is read from `profile` instead of `profile_v4_2`; the base pointer is the same allocation, but the mixed type is fragile. Several firmware copy functions store little-endian fields directly for boot clocks/voltages without explicit conversion, matching existing struct types but worth checking on non-little-endian builds.

### Test signals
Useful tests include voltage object v4 lookup with GPIO LUT, SVID2, unsupported mode, and over-limit entry counts; AVFS fixtures for 4.1, 4.2, and unsupported revisions; firmwareinfo 3.1/3.2 boot paths with successful and failing SMU clock queries; and SMC DPM table copy verification. Integration signals are Vega10 AVFS initialization, Vega12 SMC DPM parsing, boot clock reporting, and boards whose VBIOS exposes newer atomfirmware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomfwctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomfwctrl.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomfwctrl.h

### Purpose
`ppatomfwctrl.h` defines the hwmgr-facing structures and prototypes for atomfirmware-era BIOS control. It is the SOC15/Vega-style companion to the older `ppatomctrl.h` interface.

### Important APIs and types
The header defines `BIOS_CLKID`, atomfirmware master command/data table index macros, `PP_ATOMFWCTRL_MAX_VOLTAGE_ENTRIES`, and normalized output structs for voltage tables, GPIO pin assignment, SOC15 clock dividers, AVFS parameters, GPIO parameters, VBIOS boot values, and SMC DPM parameters. The SMC DPM struct is broad: it includes I2C addresses/lines, sensor presence, voltage step limits, VR mappings, phase shedding masks, telemetry limits/offsets, AC/DC and VR-hot GPIOs, LEDs, PLL/UCLK/SOCCLK/ACG spread settings, and a second VR I2C address.

Function prototypes expose GPU PLL divider calculation, voltage table and GPIO-voltage detection, AVFS/GPIO/boot/SMC DPM reads, and clock lookup by SMU clock ID.

### Control flow and state
There is no executable code. The declared functions use caller-owned output buffers and normally return `0` on success or a negative/nonzero error on missing tables, unsupported revisions, or failed command execution.

### Dependencies and integration points
The header includes `hwmgr.h` and references atomfirmware enums/struct layouts through `atomfirmware.h` in the implementation. It is consumed by Vega/SOC15 hwmgr code that needs VBIOS-derived AVFS, voltage, PLL, boot, and SMC DPM information.

### Risks and test signals
The interface has many firmware-unit fields and fixed array bounds, so regressions often appear as wrong units or partial copies rather than compile errors. `GetIndexIntoMasterCmdTable` and `GetIndexIntoMasterDataTable` depend on exact atomfirmware v2.1 master-list layouts. Tests should pair header ABI checks with implementation fixtures for v4 voltage objects, v4.1/v4.2 AVFS, firmwareinfo 3.1/3.2, and SMC DPM v4.1 structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/ppatomfwctrl.h -->
