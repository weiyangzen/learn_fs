# sources/distributed-fs/ceph-client/kernel/debug/debug_core.h

## Purpose
`debug_core.h` is the private interface between the KGDB core, GDB stub, and KDB frontend. It defines shared debugger state structures, CPU exception-state flags, special control return values, and cross-file function declarations.

## Important APIs, types, and functions
The main type is `struct kgdb_state`, which carries exception vector, signal, error code, CPU, pass-exception flag, thread query/current thread IDs, selected thread ID, registers, and optional `send_ready` synchronization pointer. `struct debuggerinfo_struct` stores per-CPU debugger info pointer, task, exception state, return state, IRQ depth, entry count, and roundup flag.

Flags include `DCPU_WANT_MASTER`, `DCPU_NEXT_MASTER`, `DCPU_IS_SLAVE`, and `DCPU_WANT_BT`. Special return values are `DBG_PASS_EVENT` for KDB/GDB mode switching and `DBG_SWITCH_CPU_EVENT` for switching the master CPU. Declarations cover software breakpoint APIs, polled I/O, `gdb_serial_stub()`, `gdbstub_msg_write()`, `gdbstub_state()`, KDB entry and parser helpers, and `kdb_dump_stack_on_cpu()`.

## Control flow
The header has no runtime flow. It provides the contracts that allow `debug_core.c` to call the selected frontend, GDB stub to hand commands to KDB, and KDB to request CPU backtraces or switch modes. When `CONFIG_KGDB_KDB` is disabled, `kdb_stub()` is an inline stub returning `DBG_PASS_EVENT`.

## State and persistence behavior
The header declares shared runtime state such as `kgdb_info`, `dbg_switch_cpu`, and `dbg_kdb_mode` but owns no storage. It has no persistence behavior.

## Dependencies and integration points
It depends on kernel task/register types through included users and is included by KGDB core, GDB stub, and KDB implementation files. It is tightly coupled to `include/linux/kgdb.h`, arch KGDB register handling, and KDB private code.

## Risks and edge cases
Because this is a private ABI among debugger components, changes to `struct kgdb_state`, flag meanings, or special return values must be reflected across all frontends. The inline KDB stub preserves buildability without KDB, but code paths must still handle `DBG_PASS_EVENT` when no alternate frontend exists.

## Test signals
Build tests should cover KGDB with and without KDB. Runtime mode-switch tests, CPU-switch tests, and GDB qRcmd-to-KDB paths exercise most of this header's shared contracts.
