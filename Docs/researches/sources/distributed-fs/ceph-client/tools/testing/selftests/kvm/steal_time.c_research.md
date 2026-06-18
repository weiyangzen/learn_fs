# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/steal_time.c

## Purpose
This cross-architecture KVM selftest validates paravirtual stolen-time reporting for x86, arm64, RISC-V, and LoongArch. It verifies registration UAPI, shared-memory status fields, monotonic versioning where applicable, and measured stolen time under forced preemption.

## Important APIs, Types, And Functions
Architecture-specific registration uses `MSR_KVM_STEAL_TIME` on x86, ARM PV_TIME SMCCC plus `KVM_ARM_VCPU_PVTIME_IPA`, RISC-V SBI STA shared-memory one-reg state, and LoongArch PVTIME device attributes. Shared structures include `struct kvm_steal_time`, arm64 `struct st_time`, RISC-V `sta_struct`, and LoongArch `struct kvm_steal_time`. Common helpers include `steal_time_init()`, `is_steal_time_supported()`, `check_steal_time_uapi()`, `do_steal_time()`, and `run_vcpu()`.

## Control Flow
`main()` pins the process and a helper thread to CPU 0, creates four vCPUs, maps a shared steal-time region at `ST_GPA_BASE`, requires architecture support, and runs UAPI validation. Each vCPU is initialized, run once to register or initialize shared memory, run again to sample baseline stolen time, then a busy helper thread steals CPU time. The vCPU is run a final time and guest-reported stolen delta must be at least the measured host run-delay delta.

## State, Dependencies, And Integration
State includes per-vCPU shared-memory pointers, guest stolen-time samples, and CPU affinity. There is no persistence. The test depends on PV-time support, identity mapping of the shared area, host scheduler behavior, and `MIN_RUN_DELAY_NS`/`get_run_delay()` selftest timing helpers.

## Risks And Test Signals
Risks include noisy scheduling, unsupported PV-time features, architecture-specific registration semantics, and timing false failures. Signals are UAPI invalid-input assertions, status-field checks, per-vCPU stolen-time comparisons, optional verbose dumps, and four TAP pass results.
