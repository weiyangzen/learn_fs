# sources/distributed-fs/ceph-client/arch/parisc/include/asm/assembly.h

Purpose: central PA-RISC assembly helper contract. It defines frame sizes, ABI constants, instruction mnemonics, space-register roles, virtual/physical conversion macros, safe bitfield macros, register save/restore blocks, and exception-frame helpers.

Important APIs/types/functions: key macros include `FRAME_SIZE`, `CALLEE_SAVE_FRAME_SIZE`, `LDCW`, `BL`, `PA_ASM_LEVEL`, `PRIV_*`, `SR_*`, `LDREG/STREG`, `tophys/tovirt`, `load32`, `loadgp`, `save_general`, `rest_general`, `save_specials`, and related pt_regs helpers.

Control flow: low-level entry code expands these macros to save register state, translate addresses, handle PA1.x versus PA2.0 instruction differences, and restore execution context.

State and persistence: it does not store state itself, but it defines the saved register-frame layout used persistently on kernel stacks. Dependencies and integration: depends on generated offsets, `page.h`, `types.h`, `asmregs.h`, and `psw.h`.

Risks and test signals: any frame-size or register-save mismatch corrupts traps, syscalls, and context switches. Test with build coverage for 32/64-bit, stack unwinder tests, syscall/trap stress, and objdump review of macro expansion.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
