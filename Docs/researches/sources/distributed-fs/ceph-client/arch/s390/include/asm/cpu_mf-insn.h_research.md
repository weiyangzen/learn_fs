<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf-insn.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf-insn.h

Purpose: Provides assembler include guards for CPU Measurement Facility instruction support.

Important APIs/types/functions: This snapshot only exposes the guarded include point for instruction-level definitions used elsewhere. Source-visible declarations include: #define _ASM_S390_CPU_MF_INSN_H.

Control flow: Assembly sources include it to share CPU-MF instruction naming and build context.

State and persistence behavior: No state.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates CPU-MF assembly implementations and perf support..

Risks: Minimal wrapper; future instruction macros must match hardware encodings.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 22 lines, 480 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpu_mf-insn.h -->
