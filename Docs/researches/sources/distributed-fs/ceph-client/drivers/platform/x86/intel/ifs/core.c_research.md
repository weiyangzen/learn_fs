<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/core.c

## Purpose
Top-level Intel IFS module initialization. It detects supported CPU models and integrity capabilities, configures per-test misc devices, and registers sysfs attribute groups.

## Important APIs, Types, And Functions
`ifs_cpu_ids[]` maps supported Sapphire Rapids, Emerald Rapids, Granite Rapids, Crestmont, and Darkmont families to array-test generations. `ifs_devices[]` describes SAF, Array BIST, and SBAF devices with test capability bits, MSR sets, and miscdevice names `intel_ifs_0`, `intel_ifs_1`, and `intel_ifs_2`. `ifs_pkg_auth` tracks per-package firmware authentication during load.

## Control Flow
`ifs_init()` first matches CPU family/model and checks `MSR_IA32_CORE_CAPS` for integrity capability exposure. It reads `MSR_INTEGRITY_CAPS`, allocates per-package auth state, then registers only devices whose integrity-cap bit is set. Generation and array generation are stored in each device's runtime data. Error cleanup deregisters any already registered misc devices.

## State And Persistence
Global `ifs_devices[]` holds per-device runtime data for loaded image, status, generation, and last details. `ifs_pkg_auth` is allocated for topology max packages and freed on module exit.

## Dependencies And Integration Points
Depends on x86 CPU matching, MSR access, miscdevice registration, attribute groups exported by `sysfs.c`, and constants/data structures from `ifs.h`.

## Risks And Test Signals
Risks include stale CPU model lists, incorrect capability-bit mapping, and registering devices with missing MSR support. Test on each supported generation by checking misc device creation matches capability bits, sysfs groups differ for array tests, and cleanup unloads all registered devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/ifs/core.c -->
