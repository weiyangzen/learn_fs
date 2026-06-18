# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/hypercalls.c

Purpose: this arm64 KVM selftest validates pseudo-firmware bitmap registers and the guest-visible SMCCC hypercall interface they control, including standard, standard-hypervisor, vendor-hypervisor, and second vendor bitmap registers.

Important APIs and data: `struct kvm_fw_reg_info` describes each firmware bitmap register, max feature bit, and reset value. `hvc_info[]` and `false_hvc_info[]` define SMCCC calls to test supported/unsupported behavior. Guest `guest_test_hvc()` and `guest_code()` validate SMCCC return values by stage. Host helpers `steal_time_init()`, `test_fw_regs_before_vm_start()`, `test_fw_regs_after_vm_start()`, `test_vm_create()`, `test_guest_stage()`, and `test_run()` coordinate register UAPI and guest stages.

Control flow: host creates a VM, initializes steal-time backing, verifies firmware register reset values and writeability before first run, clears features, then runs the staged guest. After the first sync, host verifies firmware registers are locked with `EBUSY`. It then starts a fresh VM to test default-enabled feature behavior and false feature queries.

State and persistence: global `stage` is synced to the guest. Firmware bitmap register values are KVM vCPU state. Steal-time memory is added as a guest memory region. No durable state is stored.

Dependencies and integration points: depends on arm64 SMCCC constants, KVM firmware feature bitmap one-reg ABI, private vCPU device attrs for steal time, and libkvm ucall/global sync helpers.

Risks: register max-bit constants must track KVM ABI growth. Firmware bitmap registers become immutable after vCPU run, so stage ordering is critical. Some hypercall families can have nuanced return values, but the test only asserts supported versus not-supported.

Test signals: reset-value mismatches, invalid write acceptance, missing `EBUSY`, disabled features returning supported, enabled features returning not-supported, or false feature queries succeeding are failures.
