# sources/distributed-fs/ceph-client/arch/parisc/include/asm/kgdb.h

Purpose: defines PA-RISC KGDB register layout and breakpoint integration.

Important APIs/types/functions: exports `BREAK_INSTR_SIZE`, breakpoint instruction encoding, `NUMREGBYTES`, register numbering/layout helpers, and kgdb trap declarations.

Control flow: KGDB inserts breakpoints, trap handling captures PA-RISC registers into the KGDB packet layout, and remote debugging commands restore or inspect state.

State and persistence: breakpoint-patched text and captured register packets persist during debugging sessions. Dependencies and integration: trap handling, ptrace register layout, text patching, and kgdb core.

Risks and test signals: wrong register packet layout makes remote debugging unsafe. Test with kgdb break/continue, register read/write, and single-step where supported.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
