<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dis.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/dis.h

Purpose: Declares s390 instruction-disassembly helpers.

Important APIs/types/functions: `insn_length()`, `show_code()`, `print_fn_code()`, `find_insn()`, and `is_known_insn()`. Source-visible declarations include: #define __ASM_S390_DIS_H__; static inline int insn_length(unsigned char code); struct pt_regs;; void show_code(struct pt_regs *regs);; void print_fn_code(unsigned char *code, unsigned long len);; struct s390_insn *find_insn(unsigned char *code);; static inline int is_known_insn(unsigned char *code).

Control flow: `insn_length()` derives length from the first opcode bits; other helpers decode and print code around registers or functions.

State and persistence behavior: No persistent state; decoding consumes text bytes.

Dependencies and integration points: Direct includes are #include <asm/dis-defs.h>. Integrated with Integrates oops reporting, kprobes/ftrace validation, instruction patching, and debug output..

Risks: Instruction length decoding must match z/Architecture formats or diagnostics and patch validators misparse text.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 30 lines, 636 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/dis.h -->
