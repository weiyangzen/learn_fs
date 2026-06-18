# subset-b-003512 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_pm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_pm.c

### Purpose
`amdgpu_pm.c` is the AMDGPU power-management user-interface layer. It translates sysfs, hwmon, `gpu_od`, and debugfs operations into DPM/SMU calls, while guarding hardware access with reset/suspend/runtime-PM checks. It does not implement ASIC-specific clock, voltage, fan, or sensor algorithms itself; it exposes common Linux device files and delegates policy and telemetry work to `amdgpu_dpm_*()` and ASIC callback layers.

### Important APIs, Types, And Functions
The file exports `amdgpu_pm_sysfs_init()`, `amdgpu_pm_sysfs_fini()`, and `amdgpu_debugfs_pm_init()`. Internal access guards are `amdgpu_pm_dev_state_check()`, `amdgpu_pm_get_access()`, `amdgpu_pm_get_access_if_active()`, and `amdgpu_pm_put_access()`. The main sysfs handlers cover `power_dpm_state`, `power_dpm_force_performance_level`, `pp_num_states`, `pp_cur_state`, `pp_force_state`, `pp_table`, `pp_od_clk_voltage`, `pp_features`, `pp_dpm_*`, overdrive percentages, `pp_power_profile_mode`, busy percentages, PCIe bandwidth, unique ID, thermal throttling logging, APU thermal cap, GPU/PM metrics, SmartShift power/bias, board telemetry, and PM policy files.

The attribute model is built around `struct amdgpu_device_attr` from `amdgpu_pm.h`, the local `amdgpu_device_attrs[]` table, per-attribute update callbacks such as `default_attr_update()`, `pp_dpm_clk_default_attr_update()`, `pp_dpm_dcefclk_attr_update()`, `pp_od_clk_voltage_attr_update()`, `ss_power_attr_update()`, and `ss_bias_attr_update()`, plus `amdgpu_device_attr_create_groups()` and `amdgpu_device_attr_remove_groups()`. The hwmon surface is built from `SENSOR_DEVICE_ATTR()` entries and `hwmon_attributes_visible()`. Dynamic overdrive fan-control files use local `struct od_attribute`, `struct od_kobj`, `struct od_feature_ops`, `struct od_feature_item`, `struct od_feature_container`, `struct od_feature_set`, `amdgpu_od_set_init()`, and `amdgpu_od_set_fini()`.

### Control Flow
Sysfs reads normally resolve `struct amdgpu_device` from the DRM device, call `amdgpu_pm_get_access_if_active()` for non-waking reads, delegate to a DPM reader, format into the caller buffer with `sysfs_emit()` or `sysfs_emit_at()`, and call `amdgpu_pm_put_access()`. Writes parse and validate text first, call `amdgpu_pm_get_access()` to wake the device when legal, delegate to a DPM setter or task dispatch, release runtime PM, and return either `count` or a negative errno.

Power-state control maps user text to `enum amd_pm_state_type` or `enum amd_dpm_forced_level`, then invokes `amdgpu_dpm_set_power_state()` or `amdgpu_dpm_force_performance_level()`. For forced performance levels, `stable_pstate_ctx_lock` is held and `stable_pstate_ctx` is cleared so a direct sysfs request overrides any context-owned stable pstate. `pp_force_state` parses a state index, uses `array_index_nospec()`, fetches `pp_states_info`, rejects boot/default-only states, then dispatches `AMD_PP_TASK_ENABLE_USER_STATE`.

Clock-level files share `amdgpu_get_pp_dpm_clock()` and `amdgpu_set_pp_dpm_clock()`. The setter converts a whitespace-separated set of DPM levels into a 32-bit mask through `amdgpu_read_mask()` and calls `amdgpu_dpm_force_clock_level()`. `pp_od_clk_voltage` and the `gpu_od` subfiles use bounded local copies and integer arrays to parse overdrive commands; commit commands dispatch `AMD_PP_TASK_READJUST_POWER_STATE`.

Initialization starts in `amdgpu_pm_sysfs_init()`. It exits early if already initialized or DPM is disabled. It registers hwmon unless the device is in SR-IOV multi-VF mode, chooses a visibility mask for bare metal, one-VF, or multi-VF operation, creates the common device files, optionally creates the dynamic `gpu_od` hierarchy when overdrive is supported, optionally adds `pm_policy`, and optionally adds `board` telemetry files plus extra node/baseboard power files when sensors are supported. Errors unwind created sysfs files and hwmon registration. Finalization removes dynamic OD files, unregisters hwmon, and removes tracked device files.

### State, Persistence, And Dependencies
Persistent driver state is stored under `adev->pm`: `sysfs_initialized`, `int_hwmon_dev`, `pm_attr_list`, `od_kobj_list`, `pp_force_state_enabled`, `od_feature_mask`, `pp_feature`, `stable_pstate_ctx`, fan and thermal threshold fields, and nested DPM state. Thermal throttling logging persists through `adev->throttling_logging_enabled` and `adev->throttling_logging_rs`. SmartShift bias is stored in global `amdgpu_smartshift_bias`. The sysfs/hwmon/debugfs files are persistent kernel object registrations until removal, but telemetry values are read live from PMFW/SMU through DPM calls.

Dependencies include DRM device plumbing, runtime PM, hwmon, sysfs/kobject APIs, debugfs, PCIe MPS helpers, `array_index_nospec()`, kernel string/integer parsers, AMDGPU virtualization helpers, IP-version queries, `mgpu_info`, PMFW/SMU DPM entry points from `amdgpu_dpm.h`, and clock-gating state from the wider AMDGPU device code.

### Integration Points
The file is the main bridge between userspace monitoring/tuning tools and AMDGPU PM internals. It integrates with Linux hwmon conventions for sensors and fan/power limits, DRM debugfs via `amdgpu_pm_info` and `amdgpu_pm_prv_buffer`, SR-IOV mode policy for read/write exposure, board-management telemetry, SmartShift multi-GPU discovery, DC/display clock policy through DPM functions declared elsewhere, and ASIC-specific SMU implementations that decide which operations return success or `-EOPNOTSUPP`.

### Risks
Visibility and permission logic is ASIC- and virtualization-sensitive; adding a new IP version without updating these checks can expose unsupported files or hide valid controls. Many write paths accept compact text protocols, so parser bounds, parameter counts, signedness, and commit semantics are high-risk. Some visibility checks call DPM getters/setters with sentinel values such as `NULL` or `U32_MAX`; backend implementations must treat these as capability probes, not real operations. Runtime-PM pairing must remain correct on every early return after `amdgpu_pm_get_access*()`. Manual fan and power-cap controls can affect hardware safety if backend range checks are incomplete. Dynamic kobject setup has multi-step allocation and sysfs creation; partial failure depends on `amdgpu_od_set_fini()` correctly removing all tracked entries.

### Test Signals
Useful signals include sysfs presence/permission tests across bare metal, one-VF, and multi-VF modes; runtime suspend/resume reads returning `-EPERM` or `-EBUSY` where expected; round trips for power states, forced levels, DPM masks, `pp_table`, overdrive commands, fan controls, power caps, PM policies, and APU thermal caps; hwmon visibility tests across APUs, dGPUs, multi-AID parts, no-fan boards, and unsupported sensors; fault-injection for hwmon/sysfs/kobject allocation failures; debugfs reads during reset/suspend; and backend `-EOPNOTSUPP` probes verifying that unsupported files are hidden or read-only rather than unsafe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/amdgpu_pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_dpm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_dpm.h

### Purpose
`amdgpu_dpm.h` is the central AMDGPU dynamic power-management interface header. It defines shared PM/DPM state structures and declares the public DPM wrapper functions used by sysfs, hwmon, display, reset, media, RAS, virtualization, and ASIC power-management code. It is the contract between common AMDGPU code and the underlying PowerPlay/SMU implementations.

### Important APIs, Types, And Functions
The header defines PM mode and capability enums such as `enum gfx_change_state`, `enum amdgpu_int_thermal_type`, `enum amdgpu_runpm_mode`, `enum ip_power_state`, and BACO/MACO support bits. Core data types include `struct amdgpu_ps`, `struct amdgpu_dpm_thermal`, clock/voltage dependency tables, leakage and phase-shedding tables, UVD/VCE dependency tables, `struct amdgpu_ppm_table`, `struct amdgpu_cac_tdp_table`, `struct amdgpu_dpm_dynamic_state`, `struct amdgpu_dpm_fan`, `struct amdgpu_dpm`, `struct amdgpu_smu_i2c_bus`, `struct config_table_setting`, and `struct amdgpu_pm`.

The function declarations cover sensor reads, APU thermal caps, SMU power/clock gating, SCLK/MCLK queries, XGMI and power profiles, BACO/mode/link resets, MP1 state changes, DF C-state, multi-GPU fan boost, SMU I2C access, ACPI PM events, media and JPEG/VPE enablement, SMU firmware loading, passthrough SBR, HBM bad page/channel reporting, RMA reason reporting, frequency ranges, watermarks, SMU events, GFXOFF residency and status, thermal throttling counters, ECC info, current and forced power states, PowerPlay table get/set, overdrive editing, clock-level printing/emission, PP feature masks, fan controls, power limits, metrics, display configuration, display clocks, UCLK DPM states, PM policies, SDMA/VCN reset support, temperature metrics support, and RAS SMU driver lookup.

### Control Flow
This header does not implement control flow, but it shapes common call flow. Higher layers keep state in `adev->pm`, call these `amdgpu_dpm_*()` functions with an `amdgpu_device`, and the implementation dispatches to the active PM backend. Typical flows include sysfs/hwmon reading sensors through `amdgpu_dpm_read_sensor()`, display code updating clocks and watermarks through display-configuration functions, reset paths checking and invoking BACO or mode/link resets, and overdrive paths printing clock levels, editing DPM tables, then dispatching a readjust task.

### State, Persistence, And Dependencies
`struct amdgpu_pm` is persistent per-device state. It contains mutexes, current/default clocks, I2C and EEPROM adapters, hwmon device pointer, fan metadata, DPM enablement and firmware data, display configuration, SMU private buffer, power-feature masks, per-IP power states, debug masks, stable pstate context, runtime PM mode, OD kobject list, and OD feature mask. `struct amdgpu_dpm` persists legacy PowerPlay power states, requested/current/boot/video states, platform capabilities, dynamic dependency tables, fan and thermal state, power-control limits, activity flags, and forced-level state. The many dependency table pointers require backend allocation/free discipline outside this header.

Dependencies include AMDGPU device/core types, DRM display PM types, I2C adapters, firmware and buffer objects, RAS SMU types, SMU event and temperature metric enums, PowerPlay clock/profile/sensor enums, VCE state types, and kernel synchronization primitives.

### Integration Points
The declarations are consumed by `amdgpu_pm.c`, display/DC integration, reset and runtime power management, media IP block power control, RAS/error-reporting paths, virtualization support, and ASIC-specific SMU managers. The `struct amdgpu_pm` layout is embedded in `struct amdgpu_device`, so changes affect broad driver initialization, suspend/resume, and teardown paths.

### Risks
Because this is a broad cross-module contract, layout or semantic changes can break multiple ASIC backends. Pointer-owning tables in `struct amdgpu_dpm_dynamic_state` and firmware/private-buffer fields require clear ownership outside the type definition. Many functions return `-EOPNOTSUPP` as feature probes; callers rely on consistent behavior to expose or hide user interfaces. `struct amdgpu_pm` mixes locks, kobjects, I2C buses, runtime mode, and firmware state, so initialization and teardown order matters. Adding new OD feature bits requires matching visibility and handler logic in `amdgpu_pm.c`.

### Test Signals
Compile coverage across enabled/disabled ASIC families is the first signal because this header fans out widely. Runtime signals include sysfs/hwmon capability probing, suspend/resume and runtime-PM transitions, BACO/mode reset paths, display clock changes, fan and power-limit controls, metrics retrieval, SMU I2C bus arbitration, RAS/ECC paths, and virtualization mode behavior. Static analysis should watch for uninitialized fields in `struct amdgpu_pm` and stale backend implementations after prototype changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_dpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_dpm_internal.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_dpm_internal.h

### Purpose
`amdgpu_dpm_internal.h` is a narrow internal header for common DPM implementation details. In this snapshot it exposes only the internal display-configuration helper needed within the PM/DPM implementation area.

### Important APIs, Types, And Functions
The single declaration is `void amdgpu_dpm_get_display_cfg(struct amdgpu_device *adev);`. It is intentionally not part of the broader public `amdgpu_dpm.h` interface.

### Control Flow
The header has no implementation. Its declared helper is expected to collect or refresh display-related PM configuration for an `amdgpu_device`, likely feeding the `adev->pm.pm_display_cfg` state used by DPM/display clock policy.

### State, Persistence, And Dependencies
There is no state in the header. It depends on the caller having visibility of `struct amdgpu_device`. Persistent effects, if any, are in the implementation of `amdgpu_dpm_get_display_cfg()`, not here.

### Integration Points
This header separates an implementation-private DPM helper from the external PM API. It should be included by DPM source files that need to refresh display configuration without exposing that helper to unrelated driver components.

### Risks
The main risk is interface drift: if more internal helpers are added here, the boundary between public DPM API and internal PM implementation can become unclear. Callers also need to ensure display hardware and PM state are initialized before invoking the helper.

### Test Signals
Build coverage of DPM implementation files using this declaration is the primary test signal. Runtime display reconfiguration, monitor hotplug, suspend/resume, and clock/watermark updates are indirect signals that the helper's implementation and call sites remain valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_dpm_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_pm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_pm.h

### Purpose
`amdgpu_pm.h` declares the common AMDGPU PM user-interface helpers and the metadata model for PM sysfs attributes. It is the companion header for `amdgpu_pm.c` and gives other driver code access to PM sysfs/debugfs initialization and teardown.

### Important APIs, Types, And Functions
`struct cg_flag_name` maps clock-gating flag bits to printable names for debug output. `enum amdgpu_device_attr_flags` defines feature masks such as `ATTR_FLAG_BASIC` and `ATTR_FLAG_ONEVF`; `ATTR_FLAG_TYPE_MASK`, `ATTR_FLAG_MODE_MASK`, and `ATTR_FLAG_MASK_ALL` provide mask constants. `enum amdgpu_device_attr_states` distinguishes unsupported and supported attributes. `enum amdgpu_device_attr_id` enumerates all PM sysfs attributes from `power_dpm_state` through `pm_metrics` and `device_attr_id__count`.

`struct amdgpu_device_attr` wraps a `struct device_attribute` with an attribute ID, flags, and optional `attr_update()` callback. `struct amdgpu_device_attr_entry` tracks created attributes in a list for teardown. Macros `to_amdgpu_device_attr()`, `__AMDGPU_DEVICE_ATTR()`, `AMDGPU_DEVICE_ATTR()`, `AMDGPU_DEVICE_ATTR_RW()`, and `AMDGPU_DEVICE_ATTR_RO()` generate table entries that bind names to `amdgpu_get_*` and `amdgpu_set_*` handlers. Public functions are `amdgpu_pm_sysfs_init()`, `amdgpu_pm_virt_sysfs_init()`, `amdgpu_pm_sysfs_fini()`, `amdgpu_pm_virt_sysfs_fini()`, and `amdgpu_debugfs_pm_init()`.

### Control Flow
This header does not implement control flow, but the macro-generated descriptors drive `amdgpu_pm.c` initialization. Each descriptor carries a name, mode, handler pointers, flags, and optional feature-update callback. During init, the C file evaluates the flags against the current SR-IOV/ASIC mask, lets the update callback adjust visibility or mode, creates supported files, and records them for removal.

### State, Persistence, And Dependencies
The header owns no runtime state directly. It defines the metadata objects that become persistent sysfs files once `amdgpu_pm_sysfs_init()` creates them and list entries under `adev->pm.pm_attr_list` track them. Dependencies include kernel `device_attribute`, list handling, permissions constants, fixed-width integer types, and `struct amdgpu_device`.

### Integration Points
`amdgpu_pm.c` uses this header heavily for its attribute table and lifecycle functions. Broader AMDGPU device initialization and virtualization paths call the declared sysfs/debugfs init/fini functions. Attribute IDs are also used by per-attribute update callbacks to apply ASIC- and SR-IOV-specific policy.

### Risks
The macro scheme requires exact naming alignment: `device_attr_id__<name>` and `amdgpu_get_<name>`/`amdgpu_set_<name>` must exist for each generated descriptor. Adding, removing, or renaming attributes requires updating the enum, handlers, and visibility logic together. The split between basic and one-VF flags directly affects what virtual functions can access; incorrect flags can expose unsafe tuning controls or hide required telemetry. Declared virtual sysfs functions must be implemented elsewhere to avoid link failures.

### Test Signals
Compile-time failures catch many macro naming errors. Runtime tests should enumerate expected sysfs files under different ASIC generations and SR-IOV modes, verify read/write permissions, and exercise init/fini cycles to ensure list-tracked removal remains correct. Review signals include enum/table synchronization and any new attribute's update callback coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_pm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/Makefile -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/Makefile

### Purpose
This Makefile fragment contributes legacy AMDGPU DPM manager objects to the broader AMD PowerPlay build. It keeps pre-SMU or older-family DPM code grouped under `legacy-dpm` while appending selected objects into `AMD_POWERPLAY_FILES`.

### Important APIs, Types, And Functions
The key variables are `AMD_LEGACYDPM_PATH`, `LEGACYDPM_MGR-y`, conditional `LEGACYDPM_MGR-$(CONFIG_DRM_AMDGPU_CIK)`, conditional `LEGACYDPM_MGR-$(CONFIG_DRM_AMDGPU_SI)`, `AMD_LEGACYDPM_POWER`, and the final `AMD_POWERPLAY_FILES += $(AMD_LEGACYDPM_POWER)`. Objects always include `legacy_dpm.o`; CIK support adds `kv_dpm.o` and `kv_smc.o`; SI support adds `si_dpm.o` and `si_smc.o`.

### Control Flow
Kbuild evaluates this fragment while building the AMD PM subsystem. It accumulates object names according to kernel configuration symbols, prefixes them with `../pm/legacy-dpm`, and appends them to the shared PowerPlay object list consumed by a parent makefile.

### State, Persistence, And Dependencies
There is no runtime state. Build state depends on Kconfig symbols `CONFIG_DRM_AMDGPU_CIK` and `CONFIG_DRM_AMDGPU_SI`, the parent makefile defining and later consuming `AMD_POWERPLAY_FILES`, and the listed source files existing under the legacy DPM path.

### Integration Points
This file integrates legacy DPM code into the AMDGPU PM build without making it a standalone module. It is part of the build-time boundary between common PM code and older ASIC support for SI, CIK/Kaveri-style families.

### Risks
Path or variable drift in the parent makefile can silently omit legacy DPM objects. Conditional object lists must stay aligned with Kconfig and source availability; otherwise affected ASIC families can lose power management support at build or runtime. Because objects are appended into a shared variable, ordering changes in parent fragments may affect link composition.

### Test Signals
Build tests should cover configurations with both legacy families disabled, only `CONFIG_DRM_AMDGPU_CIK`, only `CONFIG_DRM_AMDGPU_SI`, and both enabled. Link logs or `make V=1` output should show the expected legacy objects. Runtime smoke on SI/CIK hardware should verify DPM initialization and basic clock/fan telemetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/cik_dpm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/cik_dpm.h

### Purpose
`cik_dpm.h` is a small legacy DPM header for CIK/Kaveri-era power management. It exposes the Kaveri SMU IP block version object to code that registers or references the legacy SMU block.

### Important APIs, Types, And Functions
The header contains the include guard `__CIK_DPM_H__` and one external declaration: `extern const struct amdgpu_ip_block_version kv_smu_ip_block;`.

### Control Flow
There is no direct control flow. Consumers include this header to access the `kv_smu_ip_block` descriptor, which is defined in a corresponding legacy DPM/SMU source file and used by AMDGPU IP block registration.

### State, Persistence, And Dependencies
The header owns no state. The declared `kv_smu_ip_block` is a persistent constant descriptor supplied elsewhere. The declaration depends on the wider AMDGPU IP block type being visible to including translation units.

### Integration Points
This is part of the legacy DPM path built conditionally by the adjacent Makefile when CIK support is enabled. It connects legacy Kaveri SMU support to the AMDGPU IP block framework.

### Risks
The declaration must match the definition exactly; otherwise builds fail or consumers cannot register the correct SMU block. If legacy CIK support is refactored, this tiny header can become stale because it provides only a single symbol and no additional context.

### Test Signals
Compile tests with `CONFIG_DRM_AMDGPU_CIK=y` are the main signal. Runtime initialization on supported Kaveri/CIK hardware should show the SMU IP block is registered and DPM functionality is available through the common PM interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/legacy-dpm/cik_dpm.h -->
