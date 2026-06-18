<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fprobe.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fprobe.h

Purpose: Provides s390 fprobe arch constants.

Important APIs/types/functions: `FPROBE_HEADER_MSB_PATTERN`. Source-visible declarations include: #define _ASM_S390_FPROBE_H; #define FPROBE_HEADER_MSB_PATTERN 0.

Control flow: Fprobe/kprobe code uses the pattern constant when interpreting s390 function entry bytes.

State and persistence behavior: No state.

Dependencies and integration points: Direct includes are #include <asm-generic/fprobe.h>. Integrated with Integrates fprobe, kprobes, and function-entry instrumentation..

Risks: Instruction pattern constants must match actual compiler/assembler function prologues.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 10 lines, 229 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fprobe.h -->
