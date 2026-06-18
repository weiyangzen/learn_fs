# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_private.h

## Purpose
This header is the private contract shared by KDB implementation files. It defines internal command return codes, diagnostic/debug flags, machine-format strings, breakpoint structures, symbol table metadata, KDB state bits, helper macros for safe memory access, and cross-file function prototypes.

## Important APIs, Types, And Functions
Important definitions include `KDB_CMD_GO`, `KDB_CMD_CPU`, `KDB_CMD_SS`, `KDB_CMD_KGDB`, `KDB_DEBUG_*`, `KDB_MAXBPT`, `kdb_symtab_t`, `kdb_bp_t`, `kdb_dbtrap_t`, `KDB_STATE_*`, `KDB_STATE()`, `KDB_STATE_SET()`, `KDB_STATE_CLEAR()`, `KDB_SP_*`, `KDB_TSK()`, `KDB_TSKREGS()`, `GFP_KDB`, and `KDB_WORD_SIZE`. It declares the memory helpers, symbol helpers, parser helpers, command registration, breakpoint management, I/O functions, task-state helpers, and current task/register globals.

## Control Flow
There is no runtime control flow in the header, but its constants define how control flows between files. Command handlers return negative `KDB_CMD_*` values to the main loop. State bits steer debugger ownership, pager behavior, single stepping, KGDB transition, CPU hold/reentry, and keyboard entry. Memory helper macros expand variable arguments into size-aware safe-copy calls.

## State, Persistence, And Dependencies
The header exposes shared in-memory state in `kdb_state`, `kdb_nextline`, `kdb_current_task`, `kdb_current_regs`, `kdb_breakpoints`, grep globals, and prompt storage. It depends on `linux/kgdb.h` and KGDB debug core internals, so it is private to the KGDB/KDB implementation and not a stable external API.

## Integration Points
All KDB implementation files include this header. It links `kdb_debugger.c`, `kdb_main.c`, `kdb_io.c`, `kdb_keyboard.c`, support code, breakpoint code, and backtrace/module commands. It also hides optional keyboard cleanup behind a no-op macro when `CONFIG_KDB_KEYBOARD` is disabled.

## Risks
State bits are global and untyped; adding or reusing bits incorrectly can break debugger control flow. The safe memory macros take variables rather than pointers, which is convenient but easy to misuse if callers expect pointer semantics. `GFP_KDB` must match debugger context because sleeping allocation while the debug master is active can be unsafe.

## Test Signals
Build coverage across 32-bit and 64-bit architectures checks format strings and word sizes. Config combinations should include `CONFIG_KGDB_KDB`, keyboard enabled/disabled, and architectures with varying register definitions.
