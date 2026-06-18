<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_boot_cpu_id.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_boot_cpu_id.c

## Purpose
This test validates `KVM_SET_BOOT_CPU_ID`: valid BSP selection before vCPU creation, rejection of invalid IDs, and `EBUSY` once vCPU state has been created or run.

## Important APIs, Types, and Functions
Important helpers are `guest_bsp_vcpu()`, `guest_not_bsp_vcpu()`, `test_set_invalid_bsp()`, `test_set_bsp_busy()`, `create_vm()`, `run_vm_bsp()`, and `check_set_bsp_busy()`. It uses `get_bsp_flag()` from APIC helpers, `KVM_CAP_SET_BOOT_CPU_ID`, `KVM_CAP_MAX_VCPU_ID`, `vm_ioctl(KVM_SET_BOOT_CPU_ID)`, and selftests `GUEST_SYNC`/`GUEST_DONE`.

## Control Flow, State, and Persistence
`main()` requires the capability, runs VMs with BSP IDs 0 and 1, then exercises busy-state rejection. `create_vm()` validates out-of-range values, sets the BSP ID, and adds two vCPUs whose guest code asserts whether the BSP flag matches the selected ID. `run_vcpu()` also attempts to change the BSP while the VM is running and after termination. State is limited to VM boot CPU ID, vCPU IDs, APIC BSP flag, and ucall stages.

## Dependencies and Integration Points
The file integrates KVM boot CPU ID selection, APIC reset/BSP semantics, maximum vCPU ID capability, and selftests VM/vCPU creation ordering.

## Risks and Test Signals
Risks include allowing high 32-bit ID garbage, accepting IDs greater than `KVM_CAP_MAX_VCPU_ID`, or changing BSP after vCPUs exist. Signals are guest BSP flag assertions and expected `EINVAL`/`EBUSY` ioctl failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/set_boot_cpu_id.c -->
