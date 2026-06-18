# sources/distributed-fs/ceph-client/arch/x86/math-emu/fpu_arith.c

## Purpose
This file implements register-to-register x87 arithmetic instruction handlers for add, multiply, subtract, divide, reverse variants, destination variants, and pop variants.

## Important APIs, Types, and Functions
Handlers include `fadd__()`, `fmul__()`, `fsub__()`, `fsubr_()`, `fdiv__()`, `fdivr_()`, `fadd_i()`, `fmul_i()`, `fsubri()`, `fsub_i()`, `fdivri()`, `fdiv_i()`, `faddp_()`, `fmulp_()`, `fsubrp()`, `fsubp_()`, `fdivrp()`, and `fdivp_()`. They dispatch to core helpers `FPU_add()`, `FPU_mul()`, `FPU_sub()`, and `FPU_div()` using flags such as `REV` and `DEST_RM`.

## Control Flow
Each handler reads `FPU_rm`, clears C1, calls the appropriate arithmetic helper with source/destination flags and `control_word`, and for `p` variants pops the x87 stack only when the operation did not report a negative error/exception result.

## State and Persistence
The handlers mutate per-task soft-FPU registers, tags, `top`, and status bits through lower-level arithmetic helpers. No file-local state is retained.

## Dependencies and Integration Points
It is called from the `st_instr_table` in `fpu_entry.c` for ModRM register opcodes. It depends on `fpu_system.h`, `fpu_emu.h`, `control_w.h`, and `status_w.h`.

## Risks and Test Signals
Risks include wrong source/destination flag selection for reversed and pop forms, popping after failed operations, and C1 status mismatches. Test signals include x87 arithmetic instruction suites covering all register forms and stack depth changes.
