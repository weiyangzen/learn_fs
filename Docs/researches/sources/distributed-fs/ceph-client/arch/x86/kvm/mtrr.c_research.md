# sources/distributed-fs/ceph-client/arch/x86/kvm/mtrr.c

## Purpose
Implements virtual MTRR MSR get/set handling for KVM x86. It stores guest MTRR state in `vcpu->arch.mtrr_state` and validates guest writes against architectural type and reserved-bit rules.

## Important APIs, Types, and Functions
- `find_mtrr()` maps an MSR number to the correct field in the vCPU MTRR state.
- `valid_mtrr_type()` accepts architectural memory types 0, 1, 4, 5, and 6.
- `kvm_mtrr_valid()` validates default, fixed, and variable MTRR MSR payloads.
- `kvm_mtrr_set_msr()` validates and stores a writable MTRR MSR.
- `kvm_mtrr_get_msr()` returns `MSR_MTRRcap` or stored MTRR state.

## Control Flow
Set handling resolves the target MSR, rejects unknown MSRs, validates type fields and reserved physical address bits, then writes the value into per-vCPU state. Get handling synthesizes `MSR_MTRRcap` with fixed MTRRs, WC, and `KVM_NR_VAR_MTRR`, or returns the stored field for recognized writable MSRs.

## State and Persistence
State persists in `vcpu->arch.mtrr_state`: variable MTRR array, fixed 64K/16K/4K fields, and default type. The implementation does not itself recompute SPTE memory types; other MMU/vendor code consumes MTRR/PAT state when building mappings.

## Dependencies and Integration Points
Uses `asm/mtrr.h`, `cpuid.h`, and `x86.h`. Integrates with KVM MSR dispatch, CPUID physical-address restrictions via `kvm_vcpu_reserved_gpa_bits_raw()`, and memory-type logic in vendor MMU code.

## Risks
Reserved-bit validation depends on the vCPU GPA width. Incorrect fixed-range indexing or type validation can let guests program impossible MTRRs. The code returns `1` for guest-visible MSR errors, matching KVM's MSR convention rather than Linux errno.

## Test Signals
MSR tests for all fixed MTRRs, variable base/mask pairs, default type reserved bits, invalid memory types, GPA-width reserved bits, `MSR_MTRRcap` synthesis, and migration/save-restore preserving `mtrr_state`.
