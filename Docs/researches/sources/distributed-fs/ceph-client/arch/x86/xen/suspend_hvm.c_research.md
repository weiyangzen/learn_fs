<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend_hvm.c -->
# sources/distributed-fs/ceph-client/arch/x86/xen/suspend_hvm.c

## Purpose
Restores Xen HVM guest state after suspend or migration. It rebuilds shared-info and vCPU state when suspend was not cancelled, reinstalls upcall delivery, and re-runs emulated-device unplug logic.

## Important APIs, Types, And Functions
The sole exported function is `xen_hvm_post_suspend`.

## Control Flow
If the suspend completed, the function calls `xen_hvm_init_shared_info` and `xen_vcpu_restore`. It then either sets a per-CPU upcall vector for every online CPU when `xen_percpu_upcall` is enabled, or sets the global callback vector otherwise. Finally it calls `xen_unplug_emulated_devices` to restore the preferred PV device model state.

## State And Persistence
Persistent effects are reinitialized shared info mapping, restored vCPU info/callback vectors, and emulated-device unplug state. No filesystem persistence is involved.

## Dependencies And Integration Points
Depends on Xen HVM shared-info setup, upcall-vector support, online CPU iteration, and Xen feature/event helpers. It is invoked from `xen_arch_post_suspend`.

## Risks And Edge Cases
Per-CPU upcall setup is `BUG_ON` failure, so vector restore problems are fatal. Cancelled suspend skips shared-info/vCPU rebuild but still refreshes callback delivery and unplug state.

## Test Signals
Test HVM migration/save-restore with per-CPU and global callback modes, multiple online CPUs, and PV drivers loaded; inspect interrupt delivery and device enumeration after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/xen/suspend_hvm.c -->
