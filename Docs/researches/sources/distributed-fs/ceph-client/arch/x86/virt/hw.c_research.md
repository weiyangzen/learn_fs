<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/hw.c -->
# sources/distributed-fs/ceph-client/arch/x86/virt/hw.c

## Purpose
`hw.c` centralizes host CPU VMX/SVM enablement references, emergency virtualization shutdown, and KVM emergency callback registration.

## Important APIs, types, and functions
Important APIs are `x86_virt_register_emergency_callback()`, `x86_virt_unregister_emergency_callback()`, `x86_virt_get_ref()`, `x86_virt_put_ref()`, `x86_virt_emergency_disable_virtualization_cpu()`, and `x86_virt_init()`. VMX helpers allocate per-CPU root VMCS pages; SVM helpers set/clear EFER.SVME.

## Control flow
Init probes VMX and SVM, installs exactly one `virt_ops` provider, and clears VMX capability on failure. At runtime per-CPU reference counts enable virtualization on first user and disable on last put. Emergency paths set `virt_rebooting`, invoke KVM callbacks, and turn off VMX/SVM with IRQs disabled so INIT/reboot can proceed.

## State and persistence behavior
Persistent state includes `virt_ops`, exported `virt_rebooting`, per-CPU `virtualization_nr_users`, optional per-CPU `root_vmcs`, and an RCU-protected KVM callback.

## Dependencies and integration points
It depends on CPU feature probing, VMX MSRs/VMCS layout, SVM EFER bits, Intel PT VMX handling, RCU, preemption guards, and KVM exports.

## Risks and edge cases
Reference-count imbalance can leave virtualization enabled or disabled incorrectly. Emergency paths run in constrained contexts and intentionally swallow VMXOFF/STGI faults. VMX and SVM both appearing is treated as invalid.

## Test signals
Signals are KVM load/unload, CPU hotplug, reboot/crash paths, Intel PT interaction, and warnings for VMXON/VMXOFF faults or refcount misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/hw.c -->
