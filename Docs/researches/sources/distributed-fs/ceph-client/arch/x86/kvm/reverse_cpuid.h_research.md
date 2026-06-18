# sources/distributed-fs/ceph-client/arch/x86/kvm/reverse_cpuid.h

## Purpose
Maps Linux/KVM `X86_FEATURE_*` feature numbers back to CPUID leaf/index/register/bit locations for KVM guest CPUID construction and feature manipulation. It also defines KVM-only feature numbers for hardware CPUID bits not represented directly in generic cpufeatures words.

## Important APIs, Types, and Functions
- `KVM_X86_FEATURE(w, f)` encodes feature word and bit.
- Defines KVM-only or KVM-aligned feature numbers for SGX, AVX/AMX/AVX10 subleaves, speculation-control bits, constant TSC, AMD PerfMonV2, TSA bits, and MSR immediate.
- `struct cpuid_reg` describes a CPUID function, subleaf index, and output register.
- `reverse_cpuid[]` is the lookup table indexed by CPUID word.
- `reverse_cpuid_check()` compile-time validates that a feature word is hardware-defined and present in the table.
- `__feature_translate()` maps scattered kernel feature values into KVM feature words.
- `__feature_leaf()`, `__feature_bit()`, `feature_bit()`, `x86_feature_cpuid()`, and `cpuid_entry_*()` helpers get, set, clear, or change bits in `struct kvm_cpuid_entry2`.

## Control Flow
Callers pass an `X86_FEATURE_*` value. Translation normalizes scattered features, leaf/bit helpers validate the CPUID word at compile time, lookup the CPUID register tuple, and then operate on the matching field in a `kvm_cpuid_entry2`. `cpuid_entry_change()` open-codes set/clear to allow branchless code generation when possible.

## State and Persistence
No runtime mutable state exists. The persistent contract is the static mapping table and feature-number definitions, which must remain aligned with `NR_CPUID_WORDS`, `NCAPINTS`, and KVM's CPUID word enum.

## Dependencies and Integration Points
Includes UAPI KVM CPUID structs and Linux x86 cpufeature headers. Integrated by KVM CPUID filtering, feature exposure, vendor capability code, and guest CPUID manipulation helpers.

## Risks
Adding a scattered or KVM-only feature without updating translation or `reverse_cpuid[]` can make KVM manipulate the wrong guest CPUID bit. `reverse_cpuid_check()` intentionally rejects Linux-defined software feature words. Alias features need careful handling so user-visible CPUID leaves remain correct.

## Test Signals
Compile-time build coverage after adding CPUID words, unit-style tests for `cpuid_entry_set/clear/change/has`, guest CPUID exposure tests for new features, and negative build assertions for Linux-only feature words.
