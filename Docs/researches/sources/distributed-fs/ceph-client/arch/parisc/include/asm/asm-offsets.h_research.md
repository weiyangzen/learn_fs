# sources/distributed-fs/ceph-client/arch/parisc/include/asm/asm-offsets.h

Purpose: forwards PA-RISC assembly sources to the generated offsets header produced from C structure layout.

Important APIs/types/functions: this file exposes no independent definitions; it includes `generated/asm-offsets.h`.

Control flow: assembly preprocessing resolves constants such as pt_regs offsets, thread fields, and task layout from the generated header before assembling low-level entry code.

State and persistence: generated offsets persist in the build tree and must match the compiled C layout. Dependencies and integration: depends on the architecture offsets generator and all assembly code using symbolic structure offsets.

Risks and test signals: missing generation or stale offsets causes build failures or much worse register-frame corruption. Test by clean-building after structure changes and disassembling entry paths that use generated offsets.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
