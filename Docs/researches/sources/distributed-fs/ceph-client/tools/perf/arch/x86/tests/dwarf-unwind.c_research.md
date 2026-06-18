# sources/distributed-fs/ceph-client/tools/perf/arch/x86/tests/dwarf-unwind.c

## Purpose
This file supplies x86-specific sample preparation for perf's DWARF unwind tests. It captures the current user register set and copies a bounded slice of the current user stack into a `struct perf_sample` so the generic unwinder can operate on synthetic sample data.

## Important APIs, Types, and Functions
`test__arch_unwind_sample(struct perf_sample *sample, struct thread *thread)` is the exported architecture hook. It obtains the sample's `struct regs_dump`, allocates a `PERF_REGS_MAX` register buffer, loads live registers through `perf_regs_load()`, and fills `abi`, `regs`, and `mask`.

`sample_ustack()` allocates an 8192-byte buffer, reads the current stack pointer from `regs[PERF_REG_X86_SP]`, locates the containing map via `maps__find(thread__maps(thread), sp)`, bounds the copied stack to the end of the map and `STACK_SIZE`, copies bytes from the live stack, optionally unpoisons them for MemorySanitizer, and stores the result in `sample->user_stack`.

## Control Flow
The exported hook allocates and fills registers first, then delegates stack copying. Stack copying fails if allocation fails or the stack pointer is not found in the thread maps. On success, the sample receives both register and stack data; on failure, it returns `-1` after freeing the stack buffer when appropriate.

## State and Persistence
The function allocates heap buffers for registers and stack data and attaches them to the caller-owned `perf_sample`. It does not free the register buffer after assignment; ownership transfers to the sample/test cleanup path. It does not persist data outside the process.

## Dependencies and Integration Points
The file depends on perf register helpers, sample/event structures, `thread`, `map`, and `maps` APIs. It is used only when DWARF unwind support is enabled and `arch-tests.c` includes `suite__dwarf_unwind`.

## Risks and Edge Cases
The code copies live stack memory from the current process, so bad map lookup or unexpected stack pointer values cause failure. `map__end(map) - sp` assumes `sp` lies inside the map returned by `maps__find`; incorrect maps could underflow. MemorySanitizer builds need explicit unpoisoning to avoid false positives from copied stack poison. Allocation failure can leave partial sample state if register allocation succeeded but stack allocation fails.

## Test Signals
Success is a prepared sample with valid x86 register mask and non-empty stack dump suitable for unwinding. Failure debug logs distinguish register allocation, stack allocation, and stack map lookup issues.
