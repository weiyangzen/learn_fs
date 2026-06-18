# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/kvm_create_max_vcpus.c

## Purpose
This selftest validates KVM's advertised vCPU capacity limits. It reads `KVM_CAP_MAX_VCPUS` and `KVM_CAP_MAX_VCPU_ID`, raises the process file descriptor limit, then attempts to create the maximum number of vCPUs with dense IDs and, when supported, with high sparse IDs.

## Important APIs, Types, and Functions
`main()` is the test driver. `test_vcpu_creation()` creates a barebones VM with `vm_create_barebones()`, calls `__vm_vcpu_add()` for each ID, and frees the VM. It depends on `kvm_check_cap()`, `kvm_set_files_rlimit()`, `TEST_ASSERT()`, and KVM capability constants from `linux/kvm.h`.

## Control Flow
The program prints both capabilities, falls back to `KVM_CAP_MAX_VCPUS` when old kernels report no `KVM_CAP_MAX_VCPU_ID`, asserts max ID is at least max count, then creates `kvm_max_vcpus` vCPUs starting at ID 0. If IDs allow sparse placement, it repeats with IDs ending at the maximum supported vCPU ID.

## State, Dependencies, and Integration
State is only transient VM/vCPU file descriptors and the process `RLIMIT_NOFILE`. It integrates tightly with the shared `kvm_util.c` VM lifecycle and intentionally uses low-level `__vm_vcpu_add()` because successful creation is the assertion.

## Risks and Test Signals
The main risk is environmental: low file descriptor limits or host/KVM capability inconsistencies. Passing output is successful process exit after both creation passes; failures are capability assertion failures or `KVM_CREATE_VCPU` ioctl errors.
