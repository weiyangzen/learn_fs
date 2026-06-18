<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/seccomp.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/seccomp.h

**Purpose:** Defines Alpha's native seccomp audit architecture identity and syscall count for generic seccomp filtering.

**Important APIs/types/functions:** `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, and `SECCOMP_ARCH_NATIVE_NAME`.

**Control flow:** Generic seccomp code compares filter architecture tokens against `AUDIT_ARCH_ALPHA` and bounds syscall numbers by `NR_syscalls`.

**State and persistence behavior:** No local state. Seccomp state is per-task in generic code.

**Dependencies and integration points:** Depends on Alpha `unistd.h`, generic seccomp, and Linux audit UAPI.

**Risks:** Wrong audit architecture lets filters match the wrong ABI or reject valid Alpha tasks. Syscall-count drift can affect validation.

**Test signals:** Run seccomp BPF tests for allowed/denied Alpha syscalls and audit-arch mismatch handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/seccomp.h -->
