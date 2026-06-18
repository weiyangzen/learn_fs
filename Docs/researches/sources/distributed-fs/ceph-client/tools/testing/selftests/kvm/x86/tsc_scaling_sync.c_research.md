<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_scaling_sync.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_scaling_sync.c

## Purpose
This test checks that TSC scaling and synchronization remain monotonic across many concurrently created vCPUs. It targets regressions where scaled TSC values can move backward between vCPUs.

## Important APIs, Types, and Functions
Important code includes `guest_code()`, `run_vcpu()`, `pthread_spinlock_t create_lock`, `KVM_SET_TSC_KHZ`, `KVM_CAP_VM_TSC_CONTROL`, `vcpu_set_msr(MSR_IA32_TSC)`, and the shared global `tsc_sync`.

## Control Flow, State, and Persistence
`main()` creates a 20-vCPU VM, sets a test TSC frequency, and starts 20 pthreads. Each thread serializes vCPU creation under a spinlock because selftests creation is not thread-safe; the first created vCPU sets an initial TSC offset. Guests loop for a bounded TSC duration, repeatedly comparing their local TSC against the last shared TSC and reporting a sync if time regresses. Threads return failure counts, and the host sums them. State is the VM TSC frequency, one initial offset, guest shared `tsc_sync`, and per-thread failure counters.

## Dependencies and Integration Points
It integrates with KVM TSC scaling control, MSR TSC writes, concurrent vCPU execution, pthread synchronization, and ucall reporting.

## Risks and Test Signals
Risks include false positives from unsynchronized shared memory, vCPU creation races, or insufficient runtime. The signal is zero guest-reported regressions across all vCPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/tsc_scaling_sync.c -->
