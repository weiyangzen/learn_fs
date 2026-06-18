<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cmpxchg.h

## Purpose
Implements exchange, compare-exchange, masked subword atomics, 128-bit CAS support, and wait-on-change helpers.

## Important APIs, Types, And Functions
types `__u128_halves`; functions/prototypes `__cmpwait`; macros/constants `_ASM_RISCV_CMPXCHG_H`, `__arch_xchg_masked`, `__arch_xchg(sfx, prepend, append, r, p, n)`, `_arch_xchg`, `arch_xchg_relaxed(ptr, x)`, `arch_xchg_acquire(ptr, x)`, `arch_xchg_release(ptr, x)`, `arch_xchg(ptr, x)`, `xchg32(ptr, x)`, `xchg64(ptr, x)`, `__arch_cmpxchg_masked`, `__arch_cmpxchg`, `_arch_cmpxchg`, `SC_SFX(x)`, plus 20 more.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Special attention: subword exchange/compare-exchange is implemented with masked LR/SC loops, while Zacas/alternative paths are available for wider compare-exchange where supported.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `linux/bug.h`, `asm/alternative-macros.h`, `asm/fence.h`, `asm/hwcap.h`, `asm/insn-def.h`, `asm/cpufeature-macros.h`, `asm/processor.h`, `asm/errata_list.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 447 lines, 12563 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cmpxchg.h -->
