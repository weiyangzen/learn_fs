# sources/distributed-fs/ceph-client/arch/csky/abiv2/mcount.S

## Purpose

implements the C-SKY ABI v2 optimized `mcount` routine used by core kernel code

## Important APIs, Types, and Functions

Source read size: 211 lines, 3565 bytes. Includes: `linux/linkage.h`, `asm/ftrace.h`, `abi/entry.h`,
`asm/asm-offsets.h`. Assembly/global entries: `ftrace_stub`, `_mcount`, `ftrace_caller`,
`ftrace_call`, `ftrace_graph_call`, `ftrace_graph_caller`, `return_to_handler`,
`ftrace_regs_caller`, `ftrace_regs_call`, `ftrace_graph_regs_call`.

## Control Flow and Behavior

the assembly entry performs the standard C library operation using ABI v2 calling conventions and
hand-written loops or word-sized transfers

## State and Persistence

state changes are limited to destination memory for mutating routines and return registers for all
routines

## Dependencies and Integration Points

integrates with arch string headers, exported symbols when applicable, compiler builtins, ftrace for
mcount, and generic kernel library callers

## Risks and Test Signals

off-by-one, overlap, alignment, or register-clobber bugs affect the whole kernel; lib/string tests,
boot, KASAN/KCSAN, and ftrace tests are signals
