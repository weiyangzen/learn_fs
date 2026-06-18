# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/msr-index.h

## Purpose
Defines x86 Model Specific Register numbers and bit masks for tool-side code that must use the same symbolic MSR names as the kernel.

## APIs, Types, and Functions
This macro-only header covers architectural MSRs (`MSR_EFER`, syscall MSRs, APIC base, PAT, MTRR, TSC), security and mitigation controls (`MSR_IA32_SPEC_CTRL`, `ARCH_CAP_*`, `PRED_CMD_*`, `MSR_IA32_TSX_CTRL`), performance tracing and PEBS/LBR/PT MSRs, RAPL and thermal MSRs, VMX and SVM MSRs, resctrl MSRs, AMD family-specific MSRs, Centaur/VIA/Transmeta registers, and helper masks such as `PAT_VALUE()`.

## Control Flow, State, and Persistence
There is no executable flow. The file is persistent register metadata: callers use the constants when reading or writing MSRs or when interpreting saved register values.

## Dependencies and Integration
Includes `linux/bits.h` for `BIT`, `BIT_ULL`, and `GENMASK_ULL`. It integrates with KVM, perf, cpuid, virtualization, mitigation, power, and platform tooling that relies on kernel-compatible MSR names.

## Risks and Test Signals
Risks are stale values after kernel/SDM updates, incorrect bit widths on 32-bit builds, and unsafe use by code that writes control MSRs without checking CPU vendor/family/features. Test signals include compile coverage of all tool users, comparison against upstream kernel `msr-index.h`, and functional tests that read known stable MSRs while guarding feature-specific accesses.
