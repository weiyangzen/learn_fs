# sources/distributed-fs/ceph-client/arch/x86/include/asm/math_emu.h

## Purpose
Declares the minimal stack-context structure used by old x86 floating-point math emulation paths.

## Important APIs, Types, And Functions
Defines `struct math_emu_info` with `___orig_eip` and `struct pt_regs *regs`. There are no helpers.

## Control Flow
The structure models data saved around a device-not-present exception so emulation code can recover the faulting instruction pointer and register state.

## State And Persistence
State is exception-frame-local. It is not persisted beyond the emulation event.

## Dependencies And Integration Points
Depends on `asm/ptrace.h` for `pt_regs`. It integrates with legacy FPU emulation and trap handling on configurations that still build those paths.

## Risks And Edge Cases
The field layout must match stack expectations from 80386/80486-era exception handling. Any mismatch breaks instruction restart or register access.

## Test Signals
Compile coverage for math emulation configs and any legacy FPU-emulation boot or trap tests are the relevant signals.
