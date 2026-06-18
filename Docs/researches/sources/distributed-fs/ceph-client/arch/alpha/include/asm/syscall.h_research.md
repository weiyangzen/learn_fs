<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/syscall.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/syscall.h

**Purpose:** Provides generic syscall tracing/audit helpers for Alpha: syscall architecture, number, arguments, return values, and rollback.

**Important APIs/types/functions:** `syscall_get_arch`, `syscall_get_return_value`, `syscall_get_nr`, `syscall_set_nr`, `syscall_get_arguments`, `syscall_set_arguments`, `syscall_set_return_value`, and `syscall_rollback`.

**Control flow:** Helpers read and write Alpha `pt_regs` fields. Alpha uses `r0` for return value, `r19` as the error flag, `r0`/`r16`-`r20` argument conventions around syscall entry, and `orig_r0` for rollback.

**State and persistence behavior:** State is the saved register frame for the current task. No other persistence.

**Dependencies and integration points:** Depends on audit UAPI, scheduler task structs, and Alpha register layout.

**Risks:** Alpha syscall ABI differs from many architectures because success/error uses `r19`; tracing code must preserve that convention. Argument indexing mistakes break seccomp/audit/ptrace modifications.

**Test signals:** strace/ptrace syscall injection, seccomp user-notification or filter tests, audit syscall classification, and error-return tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/syscall.h -->
