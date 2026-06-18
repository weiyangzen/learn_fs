<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/audit.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/audit.c

Purpose: Registers SPARC audit syscall classes and classifies native and compat syscalls.

Important APIs and control flow: static arrays include generic syscall-class lists for directory writes, reads, writes, attribute changes, and signals. `audit_classify_arch()` identifies 32-bit SPARC compat arch when enabled. `audit_classify_syscall()` routes compat syscalls to `sparc32_classify_syscall()` and classifies native open/openat/socketcall/execve/openat2 specially, defaulting to native. `audit_classes_init()` registers native and compat class arrays at init.

State, dependencies, and risks: state is audit class registry configuration. Dependencies include generated syscall numbers, generic audit include lists, `CONFIG_COMPAT`, and `kernel.h` declarations. Risks are syscall-number table drift, missed new special syscall classes, and compat arch misclassification. Test signals are audit rules for open/read/write/chattr/signal classes, 32-bit process audit under compat, and openat2/socketcall classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/audit.c -->
