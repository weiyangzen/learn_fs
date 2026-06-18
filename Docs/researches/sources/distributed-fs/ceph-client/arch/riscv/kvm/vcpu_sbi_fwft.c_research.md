<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_fwft.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_fwft.c

## Purpose
`vcpu_sbi_fwft.c` implements the SBI Firmware Features extension for KVM. It virtualizes feature discovery, set/get calls, lock flags, and migration-visible state for currently supported FWFT features.

## Important APIs, Types, And Functions
`struct kvm_sbi_fwft_feature` describes a feature id, ONE_REG base, support probe, reset, set, and get callbacks. Implemented features include misaligned exception delegation and, on 64-bit, pointer masking PMLEN. `kvm_sbi_ext_fwft_handler()` handles guest `SBI_EXT_FWFT_SET/GET`. `kvm_sbi_ext_fwft_{init,deinit,reset}` manage per-vCPU configs. `kvm_sbi_ext_fwft_get_reg_id/get_reg/set_reg` expose state via ONE_REG.

## Control Flow
Init allocates a config array, probes each feature, and enables supported features. Guest set/get first validates that the feature is known and enabled, honors lock flags, then invokes the feature callback. ONE_REG access maps every feature to three registers: enabled, flags, and value.

## State And Persistence
State lives in allocated `fwft->configs` plus architectural config bits such as `arch.cfg.hedeleg`, `arch.cfg.henvcfg`, and probed pointer-masking capability flags. Reset clears locks and restores feature values. ONE_REG is the migration persistence surface.

## Dependencies And Integration Points
The file depends on RISC-V CSR helpers, ISA probing, `misaligned_traps_can_delegate()`, `SMNPM`, and shared KVM SBI state register plumbing. It directly writes `CSR_HEDELEG` and `CSR_HENVCFG` on in-guest set operations.

## Risks
CSR updates must distinguish live guest SBI calls from ONE_REG restore, because migration restore should update memory state without touching the currently loaded CSR unexpectedly. Lock semantics are guest-visible. Pointer-masking probing mutates HENVCFG temporarily and must preserve host expectations.

## Test Signals
Probe FWFT in guests, set/get misaligned delegation, restore ONE_REG state before first run, test lock denial, and test PMLEN 0/7/16 behavior on hosts with and without SMNPM support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_fwft.c -->
