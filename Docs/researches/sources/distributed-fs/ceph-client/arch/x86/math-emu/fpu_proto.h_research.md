# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_proto.h

## Purpose
This generated-style header declares the cross-file wm-FPU-emu functions used when not building prototypes. It is the glue that lets old C and assembly-oriented emulator files call each other without local forward declarations.

## Important APIs, Types, and Functions
The header declares functions from `errors.c`, `fpu_arith.c`, `fpu_aux.c`, `fpu_entry.c`, `fpu_etc.c`, `fpu_tags.c`, `fpu_trig.c`, `get_address.c`, `load_store.c`, polynomial files, arithmetic/register files not in this work item, and conversion/load-store helpers. It includes entry points such as `math_emulate()`, `FPU_exception()`, `FPU_add()`, `FPU_sub()`, `FPU_load_store()`, `poly_l2()`, and many `FPU_load_*`/`FPU_store_*` functions.

## Control Flow
There is no runtime control flow. Its declarations affect compile-time type checking and function linkage.

## State and Persistence
It stores no state, but the declarations expose functions that mutate the current task's soft-FPU state.

## Dependencies and Integration Points
It depends on prior definitions of `FPU_REG`, `fpu_addr_modes`, and related types from `fpu_emu.h`. The Makefile's `proto` target documents how to regenerate it with `cproto`.

## Risks and Test Signals
Risks include stale prototypes that hide ABI/type mismatches, especially for `asmlinkage`, `__user`, and tag-return conventions. Test signals include warning-free builds with stricter prototype checking and successful linkage of all emulator objects.
