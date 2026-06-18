# sources/distributed-fs/ceph-client/arch/m68k/kernel/syscalltable.S

## Purpose

`syscalltable.S` defines the m68k `sys_call_table` object consumed by syscall entry code.

## Important APIs, Types, and Functions

It exports `ENTRY(sys_call_table)` in `.rodata`. The macro `__SYSCALL(nr, entry) .long entry` converts generated syscall-table include rows into 32-bit function pointers. On no-MMU builds it aliases `sys_mmap2` to `sys_mmap_pgoff`.

## Control Flow

There is no runtime control flow in this file. At assembly time it includes `<asm/syscall_table.h>`, generated from `syscall.tbl`, and emits one longword per syscall entry.

## State and Persistence Behavior

The table is read-only runtime dispatch state. Syscall entry assembly indexes it to call C syscall handlers.

## Dependencies and Integration Points

It depends on `kernel/syscalls/Makefile` generation of `asm/syscall_table.h`, syscall wrapper names from kernel code, and entry assembly that knows table element size and numbering.

## Risks and Edge Cases

Generated table/header mismatch would dispatch wrong syscalls. The no-MMU `sys_mmap2` alias must stay aligned with the no-MMU implementation in `sys_m68k.c`.

## Test Signals

Build should fail on missing syscall symbols. Runtime syscall ABI smoke tests for common calls, `mmap2`, `cacheflush`, and thread-area syscalls verify table alignment.
