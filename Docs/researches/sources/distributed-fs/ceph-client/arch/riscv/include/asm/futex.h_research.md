<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/futex.h

## Purpose
Implements futex atomic operations in user memory using RISC-V inline assembly and exception-table fixups.

## Important APIs, Types, And Functions
functions/prototypes `arch_futex_atomic_op_inuser`, `futex_atomic_cmpxchg_inatomic`; macros/constants `_ASM_RISCV_FUTEX_H`, `__enable_user_access() do { } while (0)`, `__disable_user_access() do { } while (0)`, `__futex_atomic_op(insn, ret, oldval, uaddr, oparg)`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `linux/futex.h`, `linux/uaccess.h`, `linux/errno.h`, `asm/asm.h`, `asm/asm-extable.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 104 lines, 2483 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/futex.h -->
