# sources/distributed-fs/ceph-client/arch/x86/math-emu/get_address.c

## Purpose
This file decodes effective addresses for FPU memory operands in 32-bit, 16-bit, VM86, and segmented protected-mode addressing.

## Important APIs, Types, and Functions
Public functions are `FPU_get_address()` and `FPU_get_address_16()`. Static helpers and data include register-offset tables for `pt_regs`, VM86, and protected mode segment registers; `sib()` for SIB-byte decoding; `vm86_segment()`; and `pm_address()` for LDT descriptor base/limit/permission checks.

## Control Flow
`FPU_get_address()` decodes 32-bit ModRM/SIB/displacement forms, rejects illegal register-only FPU memory forms, enforces CS write protection in flat mode, records offset/selectors, and applies VM86 or protected-mode segment bases. `FPU_get_address_16()` handles 16-bit addressing combinations, defaulting BP-based forms to SS, masks offsets to 16 bits, then applies VM86 or protected-mode segment handling. `pm_address()` computes access limits for expand-up/down segments and rejects execute-only or non-writable write targets.

## State and Persistence
The file mutates `FPU_EIP` as it consumes displacement/SIB bytes, fills `struct address`, and updates global `access_limit` for later load/store bounds checks. It reads current task registers and LDT descriptors.

## Dependencies and Integration Points
It depends on user instruction-byte access, VM86 register layouts, LDT descriptor helpers from `fpu_system.h`, x86 segment semantics, and `math_abort()` for SIGSEGV/SIGILL-style failures. It is called by `math_emulate()` before memory load/store or reg/mem arithmetic.

## Risks and Test Signals
Risks include bad displacement sign extension, incorrect default segment selection, LDT race/permission mistakes, and EIP advancement errors. Test signals include FPU memory operand tests for all ModRM/SIB modes, 16-bit addressing, VM86 and LDT programs, and protected-mode segment limit violations.
