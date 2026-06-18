# sources/distributed-fs/ceph-client/arch/x86/math-emu/load_store.c

## Purpose
This file interprets x87 memory load, store, integer conversion, environment, control-word, status-word, BCD, and extended-real instructions.

## Important APIs, Types, and Functions
The public dispatcher is `FPU_load_store(u_char type, fpu_addr_modes addr_modes, void __user *data_address)`. It uses `type_table`, `data_sizes_16`, `data_sizes_32`, the `pop_0()` macro, and load/store helpers such as `FPU_load_single()`, `FPU_load_double()`, `FPU_load_extended()`, integer load/store variants, `FPU_load_bcd()`, `FPU_store_bcd()`, `fldenv()`, `FPU_frstor()`, `fstenv()`, and `fsave()`.

## Control Flow
The dispatcher first validates segmented access limits using 16-bit or 32-bit size tables, then checks instruction class: no stack operand, ST0 required, push required, or illegal. Load forms reserve stack space, load user memory, handle NaNs for real loads, and copy data into ST0. Store forms require ST0, perform conversion, and pop only if the store succeeded. `fisttp` temporarily forces `RC_CHOP`. Environment/control/status instructions directly load/store emulator state and often return `1` to suppress later instruction-address fixups.

## State and Persistence
It mutates the FPU register stack, tags, top pointer, control word, partial status summary bits, saved environment fields, and user memory. It temporarily changes `control_word` for truncating integer stores.

## Dependencies and Integration Points
It depends on address decoding for `type`, segmented `access_limit`, uaccess wrappers, conversion routines from `reg_ld_str.c`, exception helpers, and `math_emulate()` for dispatch. It is the main bridge between decoded FPU memory operands and emulator arithmetic state.

## Risks and Test Signals
Risks include wrong data-size tables, popping after failed stores, control-word restoration bugs, access-limit mistakes, and mismatches for `fisttp`, `fldenv`, `frstor`, `fsave`, and BCD forms. Test signals include memory load/store instruction suites, invalid user pointer tests, control/status word round trips, environment save/restore tests, and integer conversion edge cases.
