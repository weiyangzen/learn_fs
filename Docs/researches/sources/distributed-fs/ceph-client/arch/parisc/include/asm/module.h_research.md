# sources/distributed-fs/ceph-client/arch/parisc/include/asm/module.h

Purpose: defines PA-RISC module architecture metadata and relocation requirements.

Important APIs/types/functions: provides `struct mod_arch_specific` fields and module PLT/stub limits or helpers used by module loader code.

Control flow: module loading validates PA-RISC relocations, prepares architecture-specific stubs/descriptors if required, and patches module text/data.

State and persistence: module arch metadata persists while a module is loaded. Dependencies and integration: integrates with ELF relocation code, ftrace/kprobes, alternatives, and module memory permissions.

Risks and test signals: relocation or descriptor mistakes break loadable modules. Test with module load/unload, far-call relocations, ftrace-enabled modules, and `modpost` checks.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
