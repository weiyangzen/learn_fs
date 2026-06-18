# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_drv.c

## Purpose
`amdgpu_drv.c` is the AMDGPU DRM PCI driver entry point. It defines the KMS UAPI version, global module parameters, supported PCI IDs, the DRM driver and file-operation tables, PCI probe/remove/shutdown handlers, power-management callbacks, AER hooks, ioctl dispatch, fd release/flush behavior, sysfs groups, and module init/exit wiring.

## Important APIs, types, and functions
Important exported or externally visible objects include `amdgpu_ioctls_kms[]`, `amdgpu_partition_driver`, `amdgpu_drm_ioctl()`, and `amdgpu_file_to_fpriv()`. Core lifecycle functions are `amdgpu_pci_probe()`, `amdgpu_pci_remove()`, `amdgpu_pci_shutdown()`, `amdgpu_init()`, and `amdgpu_exit()`. Power management is split across `amdgpu_pmops_prepare()`, `suspend()`, `resume()`, `freeze()`, `thaw()`, `poweroff()`, `restore()`, `runtime_suspend()`, `runtime_resume()`, and `runtime_idle()`. Support helpers include `amdgpu_support_enabled()`, `amdgpu_fix_asic_type()`, `amdgpu_init_debug_options()`, `amdgpu_runtime_idle_check_display()`, `amdgpu_runtime_idle_check_userq()`, `amdgpu_flush()`, and `amdgpu_drm_release()`.

## Control flow
Module load initializes sync support, registers ATPX/ACPI handling, initializes KFD if available, taints the kernel if OverDrive is enabled, and registers the PCI driver. Probe rejects unsupported or experimental devices unless enabled, resolves SI/CIK ownership against radeon, applies ASIC quirks, rejects incompatible SME/Raven combinations, allocates `struct amdgpu_device` through DRM managed allocation, enables PCI, applies debug options, calls `amdgpu_driver_load_kms()`, registers the DRM device with retry on `-EAGAIN`, registers XCP and KFD clients, starts fbdev/client setup when display connectors exist, creates debugfs entries, and enables runtime PM when supported.

Remove runs RAS EEPROM recovery checks, unplug paths, NPS preparation, DRM unplug, runtime PM shutdown, KMS unload, PCI disable, and pending-transaction wait. IOCTLs wrap `drm_ioctl()` in runtime-PM get/put. File release shuts down per-file eviction fences and user queues before `drm_release()`. Runtime suspend refuses to proceed with active displays, active user queues, or undrained rings, then chooses PX, BOCO, BACO, or BAMACO handling. Resume restores PCI state or exits BACO and resumes the device.

## State and persistence behavior
The file owns module parameter globals for memory sizing, VM behavior, scheduling, power, display, RAS, recovery, firmware loading, user queues, and debug modes. Persistent device state is not stored on disk here; state lives in `struct amdgpu_device`, DRM file private data, runtime-PM flags, PCI power state, sysfs/debugfs registrations, and per-module globals. The KMS UAPI version is a compatibility contract exposed to userspace.

## Dependencies and integration points
This file integrates DRM core, DRM GEM, syncobj timelines, fbdev/client setup, PCI, runtime PM, ACPI/ATPX, VGA switcheroo, KFD, XCP partitions, RAS, reset/AER recovery, user queues, fdinfo, GEM, CS, VM, scheduler, BO-list, and sysfs memory-manager attribute groups. It is the central registration point for the ioctl handlers implemented across the AMDGPU driver.

## Risks and edge cases
Probe has many early exits where PCI enablement, DRM registration, KFD/XCP setup, and runtime PM state must unwind correctly. SI/CIK support depends on build options and module parameter precedence with radeon. Runtime PM can race displays, user queues, ring fences, or hot-unplug. Suspend paths must distinguish S0ix, S3, S4, BOCO, PX, BACO, and passthrough. `amdgpu_drm_ioctl()` must always release runtime PM references after errors. Release ordering for user queues and eviction fences is important because user queue resume work can otherwise outlive the file.

## Test signals
Useful signals include PCI probe/remove on supported and unsupported ASICs, SI/CIK ownership parameter tests, DRM minor registration and ioctl availability, render-node ioctl runtime-PM accounting, suspend/resume across S0ix/S3/S4/runtime modes, hot-unplug, AER recovery, user-queue-open release, active-display runtime-idle refusal, active-ring drain refusal, sysfs group creation, debugfs creation, KFD/XCP registration failures, and module unload with `mmu_notifier_synchronize()` coverage.
