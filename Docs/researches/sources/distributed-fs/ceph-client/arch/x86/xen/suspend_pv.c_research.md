<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend_pv.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/suspend_pv.c

## Purpose
Handles Xen PV-specific pre/post suspend transitions. It pins/unpins MMU pages, converts start-info MFNs to PFNs before suspend, disconnects shared-info mapping, rebuilds MFN-list structures afterward, restores shared info, and handles cancelled versus completed suspend differently.

## Important APIs, Types, And Functions
Exports `xen_pv_pre_suspend` and `xen_pv_post_suspend`.

## Control Flow
Pre-suspend pins all MMU state, converts store and console MFNs in `xen_start_info` to PFNs, requires interrupts disabled, switches `HYPERVISOR_shared_info` to `xen_dummy_shared_info`, and clears the boot fixmap mapping. Post-suspend rebuilds MFN list metadata, restores the shared-info fixmap, and either converts saved PFNs back to MFNs on cancelled suspend or resets `xen_cpu_initialized_map` and calls `xen_vcpu_restore` on real resume. It then unpins MMU state.

## State And Persistence
State touched includes `xen_start_info`, `HYPERVISOR_shared_info`, fixmap entries, p2m/MFN list structures, MMU pinning, and SMP initialized CPU masks. Effects are transient across suspend.

## Dependencies And Integration Points
Depends on Xen p2m and MMU helpers, fixmaps, shared-info mapping, SMP mask state, and `xen_arch_pre_suspend`/`post_suspend`.

## Risks And Edge Cases
MFN/PFN conversion must be paired correctly, especially for cancelled suspend. Interrupts must be disabled before shared-info is detached. SMP resume requires `xen_cpu_initialized_map` to exist. Fixmap update failures are fatal.

## Test Signals
Use PV suspend cancel and complete paths, console/store channel functionality after resume, multi-vCPU resume, and p2m consistency checks after migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend_pv.c -->
