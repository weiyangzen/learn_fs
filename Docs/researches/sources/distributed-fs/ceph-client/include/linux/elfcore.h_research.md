# sources/distributed-fs/ceph-client/include/linux/elfcore.h

Purpose: native ELF core file process/status note definitions and helper hooks for dumping register and architecture-specific extra core segments.

Important APIs/types/functions: `struct elf_siginfo`, `struct elf_prstatus_common`, `struct elf_prstatus`, `ELF_PRARGSZ`, `struct elf_prpsinfo`, `elf_core_copy_regs()`, `elf_core_copy_task_regs()`, `elf_core_copy_task_fpregs()`, and optional extra PHDR/data hooks.

Control flow: core dump generation copies signal/process metadata and register sets into ELF notes, optionally adding gate/vDSO or architecture-specific program headers/data.

State/persistence: generated ELF core file persists task state snapshots; no kernel-persistent state is declared.

Dependencies/integration: task stack/ptrace/user register types, `asm/elf.h` macros, `fs/binfmt_elf.c`, coredump params, architecture FPU and extra-PHDR implementations.

Risks/test signals: risks are register-set size mismatch, `BUG_ON` fallback on incompatible layouts, stale hard-coded task name length, and extra PHDR size/write inconsistency. Test native coredumps, FPU-heavy tasks, arch extra note/segment support, and debugger consumption.
