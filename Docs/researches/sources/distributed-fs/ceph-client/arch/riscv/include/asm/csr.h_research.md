<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/csr.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/csr.h

## Purpose
Defines RISC-V CSR numbers, status bits, exception causes, extension state masks, PMP/HSTATUS/HGATP fields, and CSR access macros.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_CSR_H`, `SR_SIE`, `SR_MIE`, `SR_SPIE`, `SR_MPIE`, `SR_SPP`, `SR_MPP`, `SR_SUM`, `SR_SPELP`, `SR_MPELP`, `SR_ELP`, `SR_FS`, `SR_FS_OFF`, `SR_FS_INITIAL`, plus 380 more.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Special attention: this file is the numeric source of truth for status bits, SATP/HGATP layout, exception and interrupt causes, PMP fields, state-enable bits, seed CSR fields, and inline CSR read/write/set/clear/swap helpers.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm/asm.h`, `linux/bits.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 611 lines, 17738 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/csr.h -->
