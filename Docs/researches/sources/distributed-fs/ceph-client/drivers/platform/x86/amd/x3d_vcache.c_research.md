# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/x3d_vcache.c

## Purpose
`x3d_vcache.c` is a small platform driver for AMD 3D V-Cache performance optimization. It exposes a sysfs control that switches firmware between frequency-preferred and cache-preferred modes through an ACPI `_DSM` method.

## Important APIs, Types, and Functions
The driver binds ACPI ID `AMDI0101` and registers a platform driver named `amd_x3d_vcache`. Module parameter `x3d_mode` selects the initial mode, defaulting to `frequency`. `struct amd_x3d_dev` stores the device, ACPI handle, mutex, and current mode. `amd_x3d_mode_switch()` is the core ACPI `_DSM` writer. `amd_x3d_mode_show()` and `amd_x3d_mode_store()` implement the `amd_x3d_mode` sysfs attribute. `amd_x3d_resume_handler()` reapplies the stored mode after resume.

## Control Flow
`amd_x3d_probe()` obtains the ACPI handle, verifies `_DSM` function `DSM_SET_X3D_MODE`, allocates state, initializes the mutex, stores driver data, parses the initial module parameter with `match_string()`, and calls `amd_x3d_mode_switch()`. Runtime sysfs writes use `sysfs_match_string()` to convert `frequency` or `cache` to the mode index and then call the same switch function. Resume reads the current in-kernel mode under the mutex and writes it back to firmware.

## State and Persistence
The only persistent-in-memory state is `curr_mode`, protected by `lock`. The selected mode is not persisted by this driver across reboot. Firmware receives the selected mode through ACPI `_DSM`, and resume reapplies the last in-kernel selection because firmware may reset during sleep.

## Dependencies and Integration Points
The file depends on ACPI `_DSM`, platform-driver matching, sysfs device groups, PM sleep callbacks, and standard kernel mutex helpers. It does not integrate with cpufreq or scheduler logic directly; it delegates actual optimization behavior entirely to firmware.

## Risks and Test Signals
`amd_x3d_mode_switch()` treats any non-NULL `_DSM` response as success and does not validate returned object type or status payload. It updates `curr_mode` after `_DSM` evaluation but before checking any firmware-level semantic result. Tests should cover invalid module parameters, sysfs accepted values and rejected values, ACPI absence, `_DSM` absence, resume reapplication, and concurrent sysfs access. A firmware mock that returns an error object would be useful to decide whether stricter result validation is required.
