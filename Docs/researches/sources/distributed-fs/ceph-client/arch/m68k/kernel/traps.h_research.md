# sources/distributed-fs/ceph-client/arch/m68k/kernel/traps.h

## Purpose

`traps.h` is the private declaration header for trap and bus-error entry points shared between m68k assembly, signal code, and trap implementation.

## Important APIs, Types, and Functions

It forward-declares `struct frame` and declares `buserr_c()`, `fpemu_signal()`, `fpsp040_die()`, and `set_esp0()` with `asmlinkage`.

## Control Flow

There is no executable control flow. The header records the calling convention expected by low-level exception entry code and FPU support routines.

## State and Persistence Behavior

No state is owned here. The implementation mutates current thread trap state, signal state, and kernel diagnostic state.

## Dependencies and Integration Points

It depends on `<linux/linkage.h>`. It integrates `traps.c` with entry assembly, 040/060 FPU support packages, and signal frame cleanup.

## Risks and Edge Cases

Signature drift would corrupt exception handling. `struct frame` is opaque here, so users must include the real frame layout before dereferencing it.

## Test Signals

Build coverage plus runtime trap, bus error, FPU emulator, and signal-return tests validate the declarations.
