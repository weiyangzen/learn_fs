# sources/distributed-fs/ceph-client/arch/x86/include/asm/msr-index.h

## Purpose
Provides the central x86 model-specific register number and bit-definition catalog used across CPU feature, mitigation, PMU, power, MTRR, machine-check, virtualization, and vendor-specific code.

## Important APIs, Types, And Functions
The file defines MSR numbers such as `MSR_EFER`, syscall MSRs, FS/GS base MSRs, FRED MSRs, `MSR_IA32_SPEC_CTRL`, `MSR_IA32_PRED_CMD`, MTRR/PAT MSRs, debug/branch tracing MSRs, PASID/CET MSRs, machine-check MSRs, RAPL/HWP/power MSRs, Intel PT/LBR/PEBS MSRs, AMD/Hygon/VIA/Centaur ranges, VMX/SVM feature MSRs, and many feature bit masks including `EFER_*`, `SPEC_CTRL_*`, `PRED_CMD_*`, `ARCH_CAP_*`, and memory type constants `X86_MEMTYPE_*`.

## Control Flow
There is no runtime flow; preprocessor constants are consumed by MSR read/write paths, CPU init, mitigation setup, perf, KVM, MCE, power drivers, and virtualization code.

## State And Persistence
No state is owned here. The constants address hardware MSR state, much of which persists until CPU reset or microcode-managed changes.

## Dependencies And Integration Points
Depends on `linux/bits.h`. It is integrated nearly everywhere x86 low-level code touches MSRs: `msr.h`, KVM, perf, speculation mitigations, microcode, RAPL, MTRR/PAT, MCE, CET, FRED, Intel PT, and vendor initialization.

## Risks And Edge Cases
Wrong numbers or masks can write the wrong CPU register, causing crashes, security exposure, or silent misconfiguration. Vendor-specific overlap and reserved bits require careful naming. Newly added bits must match SDM/PPR documentation and users must mask reserved fields.

## Test Signals
Broad x86 boot coverage, MSR selftests, KVM CPUID/MSR tests, perf tests, mitigation sysfs validation, powercap/RAPL tests, MCE injection, and vendor build coverage are required signals.
