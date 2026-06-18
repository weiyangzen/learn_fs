# sources/distributed-fs/ceph-client/arch/microblaze/kernel/module.c

Purpose: applies MicroBlaze ELF relocations for loadable modules and performs final cache maintenance after module load.

Important APIs and state: `apply_relocate_add()` handles `R_MICROBLAZE_32`, `R_MICROBLAZE_64`, `R_MICROBLAZE_64_PCREL`, and no-op relocation types. `module_finalize()` flushes dcache.

Control flow: relocation iteration computes `value = sym->st_value + addend`, finds the target section address, and patches either full 32-bit words or split high/low immediate instruction pairs. Unknown relocation types return `-ENOEXEC`.

State and persistence: mutates module text/data in memory. No persistent module-private state is kept here.

Dependencies and integration: used by the kernel module loader; depends on MicroBlaze ELF relocation encodings and cache flush routines.

Risks and test signals: split relocations must preserve opcode high halves and correctly compute PC-relative offsets from `location + 4`. Test module loading with absolute, long-call, and PC-relative references; verify executable module text after cache flush.
