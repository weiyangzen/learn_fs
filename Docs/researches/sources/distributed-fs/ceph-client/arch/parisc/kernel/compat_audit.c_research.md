<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/compat_audit.c -->
# sources/distributed-fs/ceph-client/arch/parisc/kernel/compat_audit.c

Source read size: 28 lines, 524 bytes.

Purpose: provides 32-bit PA-RISC audit syscall class arrays for 64-bit kernels with compat support. Important exports: `parisc32_dir_class`, `parisc32_chattr_class`, `parisc32_write_class`, `parisc32_read_class`, and `parisc32_signal_class`. Control flow: arrays are built from generic audit include lists and registered by `audit.c` during audit class initialization. State and persistence: class tables are static read-mostly data for audit rule matching. Dependencies and integration points: `linux/audit_arch.h`, generated syscall numbers, generic audit class headers, and `audit.c`. Risks: table mismatch with 32-bit syscall numbering produces incorrect audit filtering for compat tasks. Test signals: 32-bit userspace audit tests on a 64-bit kernel, write/read/chattr/signal rule matching, and build coverage with `CONFIG_AUDIT` and `CONFIG_COMPAT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/kernel/compat_audit.c -->
