<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_hsm.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_hsm.c

## Purpose
`vcpu_sbi_hsm.c` implements the SBI Hart State Management extension for KVM vCPUs: start, stop, status, and retentive suspend handling.

## Important APIs, Types, And Functions
`kvm_sbi_hsm_vcpu_start()`, `kvm_sbi_hsm_vcpu_stop()`, and `kvm_sbi_hsm_vcpu_get_status()` operate on vCPU MP state. `kvm_sbi_ext_hsm_handler()` decodes SBI function ids. `vcpu_sbi_ext_hsm` registers the extension.

## Control Flow
Start resolves the target hart id, locks its `mp_state_lock`, verifies it is stopped, stores reset pc/a1, and powers it on. Stop locks the current vCPU and powers it off if not already stopped. Status returns stopped, suspended when generic blocking is set, or started. Retentive suspend maps to KVM WFI; non-retentive suspend is unsupported.

## State And Persistence
The file mutates vCPU MP state and reset state. It does not persist to disk; reset pc/a1 and MP state are part of VM/vCPU runtime and migration state elsewhere.

## Dependencies And Integration Points
It integrates with KVM vCPU lookup, `mp_state_lock`, `kvm_riscv_vcpu_sbi_request_reset()`, power on/off helpers, and WFI blocking.

## Risks
Start/stop races depend on correct lock use. Invalid hart ids and already-started harts must return SBI errors rather than Linux errno. Status uses `stat.generic.blocking` as a suspended signal, which is an approximation.

## Test Signals
SBI HSM guest tests should start secondary vCPUs, reject duplicate starts, stop and restart harts, query status during WFI, and validate suspend return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_hsm.c -->
