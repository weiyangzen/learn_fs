<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn-asm.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn-asm.h

Purpose: Defines assembler macros that emit vector instruction encodings for toolchains lacking direct mnemonic support.

Important APIs/types/functions: `GR_NUM`, `VX_NUM`, `RXB`, `MRXB`, and vector instruction macros for load/store, permute, arithmetic, Galois-field, shift, replicate, merge, and zero/one generation. Source-visible declarations include: #define __ASM_S390_FPU_INSN_ASM_H.

Control flow: Assembler macros map register names to numeric fields, compute RXB extension bits for vector registers 16-31, and emit `.word`/`.byte` instruction encodings.

State and persistence behavior: State is generated machine code in assembly objects, not runtime data.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates `fpu-insn.h`, crypto/vector assembly, binutils compatibility, and kernel FPU sections..

Risks: Encoding bugs are catastrophic and may only appear on older assembler configurations; RXB and operand field placement are the key risk.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 754 lines, 15770 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/fpu-insn-asm.h -->
