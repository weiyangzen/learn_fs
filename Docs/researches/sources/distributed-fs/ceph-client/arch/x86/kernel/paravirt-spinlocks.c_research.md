# sources/distributed-fs/ceph-client/arch/x86/kernel/paravirt-spinlocks.c

## Purpose
Supplies x86 paravirtual spinlock defaults and feature capability setup. It lets hypervisors replace native queued spinlock unlock and vCPU preemption checks while keeping native fallback behavior.

## APIs, Types, And Functions
Exports `virt_spin_lock_key` as a static key and, under `CONFIG_PARAVIRT_SPINLOCKS`, `pv_ops_lock`. Important functions are `native_pv_lock_init()`, `__native_queued_spin_unlock()`, `pv_is_native_spin_unlock()`, `__native_vcpu_is_preempted()`, `pv_is_native_vcpu_is_preempted()`, and `paravirt_set_cap()`.

## Control Flow
On SMP, `native_pv_lock_init()` enables `virt_spin_lock_key` when the boot CPU advertises a hypervisor. `pv_ops_lock` defaults to native queued spin lock slowpath/unlock, no-op wait/kick hooks, and a native `vcpu_is_preempted` implementation returning false. `paravirt_set_cap()` forces `X86_FEATURE_PVUNLOCK` and `X86_FEATURE_VCPUPREEMPT` only when the paravirt operation pointers have been replaced from the native thunks.

## State And Persistence
State is mostly static-call/jump-label configuration and the global paravirt lock ops table. Once capabilities are forced during boot, they persist as CPU feature bits.

## Dependencies And Integration
Depends on qspinlock, static keys, paravirt call thunks, and CPU feature setup. Hypervisor-specific code can patch `pv_ops_lock`; lock slowpaths and scheduler preemption heuristics consume the resulting operations.

## Risks And Test Signals
Wrong native-vs-paravirt detection can advertise PV unlock/preemption capabilities incorrectly. Because this touches lock primitives, regressions show as hangs or poor performance under virtualization. Test signals include boot feature flags, lock stress under KVM/Xen/Hyper-V, and tracing that confirms PV wait/kick hooks are active only when intended.
