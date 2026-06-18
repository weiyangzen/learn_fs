# sources/distributed-fs/ceph-client/arch/parisc/include/asm/compat.h

Purpose: defines PA-RISC 32-bit compatibility ABI types and structures used when a 64-bit kernel runs 32-bit userspace.

Important APIs/types/functions: provides `compat_mode_t`, `compat_ipc_pid_t`, `compat_nlink_t`, `compat_stat`, `compat_sigcontext`, IPC64 structures, `COMPAT_ELF_NGREG`, `compat_elf_gregset_t`, `__is_compat_task()`, and `is_compat_task()`.

Control flow: syscall, signal, ptrace, and ELF code query task personality/flags and marshal data through these compat layouts.

State and persistence: structures define persistent user-visible ABI memory layouts; no private runtime state is stored. Dependencies and integration: includes generic compat support, scheduler/task headers, and thread-info flags.

Risks and test signals: layout drift breaks 32-bit userspace on 64-bit kernels. Test with compat syscall suites, 32-bit signal delivery, IPC stat calls, ptrace register dumps, and ELF core generation.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
