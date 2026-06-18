<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/audit.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/audit.c

Source read size: 83 lines, 1964 bytes.

Purpose: implements PA-RISC audit syscall and class classification. Important APIs/functions: audit class arrays for write/read/dir-write/chattr/signal, `audit_classify_arch()`, `audit_classify_syscall()`, and `audit_classes_init()`. Control flow: syscall classification recognizes open/openat/execve/openat2 specially, returns compat classification for 32-bit ABI under `CONFIG_COMPAT`, and registers native plus optional 32-bit audit classes at init. State and persistence: audit class registrations persist for audit subsystem lifetime. Dependencies and integration points: generic audit class include lists, `asm/unistd.h`, `compat_audit.c`, audit core. Risks: syscall-number drift or missing compat class registration causes incorrect audit rules and records. Test signals: audit rule tests for open/exec, compat 32-bit syscall audit, openat2 classification, and boot audit class registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/audit.c -->
