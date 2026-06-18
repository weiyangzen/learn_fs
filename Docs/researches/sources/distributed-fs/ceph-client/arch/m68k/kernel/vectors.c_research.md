# sources/distributed-fs/ceph-client/arch/m68k/kernel/vectors.c

## Purpose

`vectors.c` owns the m68k exception vector table and initializes early and full trap vector routing.

## Important APIs, Types, and Functions

It defines `e_vector vectors[256]`, declarations for low-level assembly handlers `system_call`, `buserr`, `trap`, `nmihandler`, and optional `fpu_emu`, plus `base_trap_init()` and `trap_init()`. It also defines a minimal Amiga NMI handler that immediately `rte`s.

## Control Flow

`base_trap_init()` optionally saves the Sun3x PROM VBR, sets the CPU VBR to `vectors`, installs the 68060 unimplemented-integer-instruction ISP vector if needed, and assigns early bus error, illegal instruction, and syscall vectors. `trap_init()` fills autovectors with `bad_inthandler`, fills unset privileged vectors with `trap`, fills user vectors with `bad_inthandler`, installs FPU emulator or 040/060 FPSP/IFPSP vectors when configured, and replaces Amiga level-7 NMI with the ignore handler.

## State and Persistence Behavior

The vector table is persistent runtime dispatch state. VBR is programmed to point at it, and individual entries are later modified by IRQ setup and FPU/platform logic.

## Dependencies and Integration Points

It depends on entry assembly labels, `bad_inthandler`, CPU/FPU feature macros, FPU support package labels, Sun3x PROM state, and `ints.c` for later interrupt vector updates. `vectors.h` exposes `base_trap_init()` to `head.S`.

## Risks and Edge Cases

`base_trap_init()` must run very early because 68060 or FPU emulation may trap before full trap initialization. Missing FPSP/IFPSP labels in the build would fail linking for 040/060 hardware-FPU configs. Filling user vectors with bad handlers means user interrupt ranges must be explicitly enabled later.

## Test Signals

Boot should reach `base_trap_init()` before early probe traps. Illegal instruction, syscall, bus error, FPU exception, and autovector tests should route to the expected handlers. IRQ request/free should visibly update entries initialized here.
