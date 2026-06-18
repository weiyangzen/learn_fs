<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kgdb.h

## Purpose
x86 KGDB register numbering, breakpoint instruction, buffer sizing, and low-level trap declarations. The header is 92 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/ptrace.h>`

Notable constants/macros: `#define _ASM_X86_KGDB_H`; `#define BUFMAX 1024`; `#define GDB_ORIG_AX 41`; `#define DBG_MAX_REG_NUM 16`; `#define NUMREGBYTES ((GDB_GS+1)*4)`; `#define GDB_ORIG_AX 57`; `#define DBG_MAX_REG_NUM 24`; `#define NUMREGBYTES ((17 * 8) + (5 * 4))`; `#define BREAK_INSTR_SIZE 1`; `#define CACHE_FLUSH_IS_SAFE 1`; `#define GDB_ADJUSTS_BREAK_OFFSET`

Notable declarations and inline helpers: `#define _ASM_X86_KGDB_H`; `#define BUFMAX 1024`; `enum regnames {`; `#define GDB_ORIG_AX 41`; `#define DBG_MAX_REG_NUM 16`; `#define NUMREGBYTES ((GDB_GS+1)*4)`; `#define GDB_ORIG_AX 57`; `#define DBG_MAX_REG_NUM 24`; `#define NUMREGBYTES ((17 * 8) + (5 * 4))`; `static inline void arch_kgdb_breakpoint(void)`; `#define BREAK_INSTR_SIZE 1`; `#define CACHE_FLUSH_IS_SAFE 1`; `#define GDB_ADJUSTS_BREAK_OFFSET`; `extern int kgdb_ll_trap(int cmd, const char *str,`; `struct pt_regs *regs, long err, int trap, int sig);`

## Control Flow
KGDB maps pt_regs to GDB register order, plants int3 breakpoints, and handles low-level serial/debug trap commands through kgdb_ll_trap().

## State and Persistence
State is debugger connection state, saved registers, and breakpoint patch sites managed by KGDB core.

## Dependencies and Integration Points
Depends on ptrace registers, int3 handling, cache coherency assumptions, and 32/64-bit GDB remote protocol layouts.

## Risks
Risks include wrong register numbering, breakpoint offset adjustment, conflicts with kprobes/ftrace, and unsafe debugging in NMI-like contexts.

## Test Signals
Tests should connect gdb over kgdboc, read/write registers, set breakpoints, single-step, test 32/64-bit layouts, and coexist with kprobes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kgdb.h -->
