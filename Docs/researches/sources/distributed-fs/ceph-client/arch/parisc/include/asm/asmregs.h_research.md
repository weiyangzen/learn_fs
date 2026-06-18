# sources/distributed-fs/ceph-client/arch/parisc/include/asm/asmregs.h

Purpose: names PA-RISC general, space, floating-point, and control registers for assembly readability.

Important APIs/types/functions: defines assembler aliases for ABI registers such as `rp`, `arg0`-`arg7`, `dp/gp`, `ret0`, `sp`, raw `r0`-`r31`, `sr0`-`sr7`, `fr0`-`fr31`, and control registers.

Control flow: there is no executable flow; assembly files include this header so register use remains readable and consistent with PA-RISC ABI conventions.

State and persistence: no state is stored, but aliases affect every assembled instruction using them. Dependencies and integration: included by `assembly.h` and low-level boot, trap, syscall, and context-switch sources.

Risks and test signals: alias drift can make assembly silently use the wrong hardware register. Test through assembler preprocessing and objdump inspection of exception and boot paths.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
