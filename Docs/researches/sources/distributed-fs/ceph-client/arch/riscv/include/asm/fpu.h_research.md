<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/fpu.h

## Purpose
Declares kernel floating-point begin/end hooks and maps availability to RISC-V F/D support.

## Important APIs, Types, And Functions
functions/prototypes `kernel_fpu_begin`, `kernel_fpu_end`; macros/constants `_ASM_RISCV_FPU_H`, `kernel_fpu_available() has_fpu()`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm/switch_to.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 16 lines, 291 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/fpu.h -->
