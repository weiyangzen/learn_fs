# sources/distributed-fs/ceph-client/drivers/firmware/smccc/kvm_guest.c

## Purpose
`kvm_guest.c` discovers ARM SMCCC KVM vendor hypervisor services and exposes service availability to guest code. On arm64 it can also discover target CPU implementation identity supplied by the hypervisor for errata handling.

## Important APIs And Functions
- Global bitmap `__kvm_arm_hyp_services` stores KVM service bits after init.
- `kvm_init_hyp_services()` checks the KVM hypervisor UUID, calls the KVM features function, and populates the bitmap.
- `kvm_arm_hyp_service_available()` tests service availability and is exported.
- `kvm_arm_target_impl_cpu_init()` discovers implementation CPU version/count/IDs and calls `cpu_errata_set_target_impl()` on arm64.

## Control Flow
PSCI calls `kvm_init_hyp_services()` after SMCCC discovery. The function first verifies the hypervisor UUID through `arm_smccc_hypervisor_has_uuid()`, invokes KVM feature discovery, converts four result registers into a bitmap, logs detected services, and lets architecture code initialize additional hypervisor services. The target implementation path checks required service bits, validates version major 1, allocates early memory for CPU implementation descriptors, queries each CPU, and either installs them for errata matching or frees memory on failure.

## State And Persistence
The service bitmap is `__ro_after_init`, so it becomes immutable after initialization. Target implementation data is allocated from memblock for early boot and retained if accepted by CPU errata code.

## Dependencies And Integration Points
It depends on SMCCC 1.1 invocation, hypervisor UUID discovery, PSCI version encoding macros, memblock, and architecture hypervisor/errata hooks. It is meaningful only under KVM/ARM hypervisors exposing the vendor interface.

## Risks
Feature bitmap interpretation depends on `ARM_SMCCC_KVM_NUM_FUNCS`. Unsupported target implementation versions are ignored. Failed partial CPU discovery must free memblock allocations. If the hypervisor advertises services incorrectly, downstream code may assume unavailable behavior.

## Test Signals
Under KVM, logs should show detected hypervisor services. `kvm_arm_hyp_service_available()` should match advertised feature bits. On arm64 with target implementation support, logs should show CPU count or warnings for unsupported/failed discovery.
