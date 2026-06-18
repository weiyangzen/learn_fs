## `sources/distributed-fs/ceph-client/arch/x86/ia32/audit.c`

Purpose: provides audit syscall classes and classification for 32-bit compatibility syscalls on x86.

Important APIs and data: arrays `ia32_dir_class`, `ia32_chattr_class`, `ia32_write_class`, `ia32_read_class`, and `ia32_signal_class` are populated from generic audit syscall class include files and terminated by `~0U`. `ia32_classify_syscall()` maps specific 32-bit syscall numbers to audit categories.

Control flow: classification switches on syscall number and returns specialized classes for `open`, `openat`, `socketcall`, `execve`, `execveat`, and `openat2`; all others return `AUDITSC_COMPAT`.

State and persistence: static read-mostly class arrays; no mutable runtime state.

Dependencies and integration points: Linux audit core, `asm/unistd_32.h` syscall numbers, and `asm/audit.h`. Used when auditing compat tasks on x86-64 or IA32 emulation paths.

Risks: missing new compat syscalls in classification can reduce audit specificity. The include-generated arrays must align with 32-bit syscall numbering.

Test signals: audit records for 32-bit compat open/exec/socket syscalls, build with `CONFIG_IA32_EMULATION` and `CONFIG_AUDIT`, and syscall-table updates checked against audit mappings.
