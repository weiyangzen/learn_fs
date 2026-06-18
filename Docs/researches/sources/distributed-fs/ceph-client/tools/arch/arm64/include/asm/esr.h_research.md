# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/esr.h

## Purpose
Defines arm64 Exception Syndrome Register encodings for tools and kernel-adjacent code that decodes traps, aborts, system-register accesses, MOPS, SME, CFI breakpoints, and ERET traps.

## Important APIs, Types, and Functions
Exports exception-class constants, EC/IL/ISS/ISS2 extraction macros, abort status bits and fault-code helpers, system-instruction ISS encoders such as `ESR_ELx_SYS64_ISS_SYS_VAL()`, CP15 conversion macros, MOPS register extractors, and inline classifiers `esr_is_data_abort()`, `esr_is_cfi_brk()`, `esr_fsc_is_translation_fault()`, `esr_fsc_is_permission_fault()`, `esr_fsc_is_access_flag_fault()`, `esr_iss_is_eretax()`, and `esr_iss_is_eretab()`. It declares `esr_get_class_string()`.

## Control Flow, State, and Persistence
All behavior is pure macro/inline decoding. Callers pass an ESR value, mask EC or ISS fields, and branch on the decoded fault or trap category. No persistent state is kept.

## Dependencies and Integration Points
Depends on `asm/sysreg.h`, `asm/types.h`, bit masks, and CFI break immediate constants supplied elsewhere. Integrates with trap reporting, KVM/system-register emulation, fault classification, and debug output.

## Risks and Test Signals
Risk is architectural drift: ISS2 and newer exception classes such as MOPS, SME, GCS, overlay, and dirty-bit faults must match the Arm ARM. Test signals include unit-style decode checks for representative ESR values, KVM sysreg trap emulation, fault handler classification, and build coverage in both assembler-excluded and C paths.
