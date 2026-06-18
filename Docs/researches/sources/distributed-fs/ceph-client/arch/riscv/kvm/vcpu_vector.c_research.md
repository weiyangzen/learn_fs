<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_vector.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_vector.c

## Purpose
`vcpu_vector.c` manages RISC-V vector extension state for KVM vCPUs, including allocation, reset, lazy save/restore, and ONE_REG access to vector CSRs/registers.

## Important APIs, Types, And Functions
Under `CONFIG_RISCV_ISA_V`, it defines vector reset, guest/host vector save/restore, vector context allocation/free, and helper cleanup. `kvm_riscv_vcpu_vreg_addr()` maps ONE_REG ids to vector CSR fields or per-register data. `kvm_riscv_vcpu_get_reg_vector()` and `set_reg_vector()` copy state to/from userspace.

## Control Flow
Reset disables VS bits, sets `vlenb`, and either zeroes allocated vector state and marks initial state or marks vector off when the guest ISA lacks V. Save only writes dirty guest state; restore skips off state. ONE_REG access first verifies guest V availability, validates sizes, and computes addresses inside `vector.datap`.

## State And Persistence
Per-vCPU guest and host contexts own vector data buffers sized by `riscv_v_vsize`. CSRs and 32 vector registers are migration-visible through ONE_REG. `vlenb` is read-only in practice and must match host-derived value.

## Dependencies And Integration Points
It depends on host vector support, guest ISA bitmaps, vector assembly helpers, KVM vCPU create/destroy paths, and userspace migration code.

## Risks
Buffer allocation must be paired and freed on partial failure. Register size validation must use `riscv_v_vsize / 32`. Saving/restoring when VS is dirty/clean/off must preserve guest lazy-vector semantics and not leak host vector state.

## Test Signals
Run vector-enabled guests, migration with vector registers, negative ONE_REG size tests, no-V guest tests, and host vector stress during KVM entry/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_vector.c -->
