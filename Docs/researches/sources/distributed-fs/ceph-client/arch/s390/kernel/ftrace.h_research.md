# sources/distributed-fs/ceph-client/arch/s390/kernel/ftrace.h

## Purpose
Defines the s390 ftrace hotpatch trampoline layout and linker-provided trampoline symbols used by `ftrace.c`.

## Important APIs, Types, And Functions
`struct ftrace_hotpatch_trampoline` contains a `brasl` opcode/disp pair, padding, the address of the rest of the intercepted function, and the interceptor address. Externs identify vmlinux trampoline ranges and shared branch/exrl trampoline code ranges.

## Control Flow
No code executes. `ftrace.c` writes instances of this packed structure and branches through the shared trampoline code to reach the selected ftrace interceptor.

## State And Persistence
Trampoline memory becomes live executable patch state. The packed layout must match linker script and assembly expectations.

## Dependencies And Integration Points
Depends on s390 integer types and ftrace linker symbols. Integrates with module architecture trampoline allocation and `asm/ftrace.lds.h` size checks.

## Risks And Edge Cases
Any layout change must update size constants and generated code. Branch displacement calculations assume field offsets and instruction sizes. Packed alignment is part of the runtime ABI between C and assembly.

## Test Signals
Signals include `BUILD_BUG_ON` size checks, ftrace initialization, module ftrace tests, and disassembly of generated trampolines.
