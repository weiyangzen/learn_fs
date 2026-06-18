# sources/distributed-fs/ceph-client/arch/x86/math-emu/Makefile

## Purpose
This Makefile builds the wm-FPU-emu software x87 emulator for x86 systems that need math emulation. It collects C and assembly emulator objects and applies emulator-specific compiler/assembler flags.

## Important APIs, Types, and Functions
Build variables are `DEBUG`, `PARANOID`, `ccflags-y`, `asflags-y`, `C_OBJS`, `A_OBJS`, and `obj-y`. The optional `proto` target regenerates `fpu_proto.h` with `cproto`.

## Control Flow
Kbuild includes this Makefile when math emulation is enabled. It compiles the listed C files for decode, arithmetic, load/store, constants, conversion, comparison, and transcendental operations, plus assembly files for unsigned arithmetic, normalization, rounding, square root, shifts, and extended-significand math.

## State and Persistence
The Makefile has no runtime state. It persists build composition and default `PARANOID` checking policy into the compiled emulator objects.

## Dependencies and Integration Points
It depends on x86 kbuild, the `$(MATH_EMULATION)` flag, 32-bit assembler conventions, and the source files in the same directory. The object list is the integration map for the whole soft-FPU subsystem.

## Risks and Test Signals
Risks include missing an object from `obj-y`, stale generated prototypes, and mismatched flags between C and assembly. Test signals are successful math-emulation builds, absence of undefined emulator symbols, and runtime execution on no-FPU or forced-emulation paths.
