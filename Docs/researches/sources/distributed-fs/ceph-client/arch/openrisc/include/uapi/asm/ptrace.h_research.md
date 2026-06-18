<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/ptrace.h

## Purpose
Defines the userspace-visible OpenRISC ptrace register layout.

## Important APIs, Types, And Functions
`struct user_regs_struct` contains 32 GPRs plus `pc` and `sr`. `struct __or1k_fpu_state` contains `fpcsr`.

## Control Flow
No control flow. `kernel/ptrace.c`, core dumps, and debuggers serialize/deserialize these layouts.

## State And Persistence
Defines ptrace and core-dump state persisted across debugger reads and core files.

## Dependencies And Integration Points
Included by UAPI ELF and signal context headers. Must match `genregs_get()` and `genregs_set()` behavior.

## Risks
Any layout change is an ABI break. User writes to SR are intentionally constrained by kernel ptrace code.

## Test Signals
`PTRACE_GETREGSET`/`SETREGSET`, GDB register display, and core dump register-set tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/uapi/asm/ptrace.h -->
