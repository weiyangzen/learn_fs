<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/audit.c -->
## sources/distributed-fs/ceph-client/arch/alpha/kernel/audit.c

**Purpose:** Registers Alpha syscall audit classes and classifies selected syscall numbers for the audit subsystem.

**Important APIs/types/functions:** `dir_class`, `read_class`, `write_class`, `chattr_class`, `signal_class`, `audit_classify_arch`, `audit_classify_syscall`, and `audit_classes_init`.

**Control flow:** At initcall time, generic audit class bitmaps are registered. Runtime syscall classification maps Alpha `open`, `openat`, `openat2`, and `execve` to specific audit classes; all others are native.

**State and persistence behavior:** The audit subsystem retains registered class tables. This file owns only static class arrays.

**Dependencies and integration points:** Depends on generic audit class include fragments and Alpha syscall numbers.

**Risks:** Incomplete classification can reduce audit rule precision. `audit_classify_arch` returns zero, so arch discrimination relies on higher-level audit arch handling.

**Test signals:** Audit rule tests for open/exec/write/read/chattr/signal classes and syscall-number drift checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/kernel/audit.c -->
