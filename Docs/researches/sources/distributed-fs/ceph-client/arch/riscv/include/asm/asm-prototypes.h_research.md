<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-prototypes.h

## Purpose
Publishes RISC-V assembly routine prototypes to C and module symbol/version generation.

## Important APIs, Types, And Functions
types `pt_regs`; functions/prototypes `__lshrti3`, `__ashrti3`, `__ashlti3`, `enter_vector_usercopy`, `xor_regs_2_`, `xor_regs_3_`, `xor_regs_4_`, `xor_regs_5_`, `riscv_v_context_nesting_start`, `riscv_v_context_nesting_end`, `ret_from_fork_kernel`, `ret_from_fork_user`, plus 3 more; macros/constants `_ASM_RISCV_PROTOTYPES_H`, `DECLARE_DO_ERROR_INFO(name) asmlinkage void name(struct pt_regs *regs)`.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
Direct includes are `linux/ftrace.h`, `asm-generic/asm-prototypes.h`. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 63 lines, 2407 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-prototypes.h -->
