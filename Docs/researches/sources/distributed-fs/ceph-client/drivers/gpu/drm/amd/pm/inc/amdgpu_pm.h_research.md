# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/inc/amdgpu_pm.h

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
