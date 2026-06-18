<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheinfo.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheinfo.h

## Purpose
Connects RISC-V cache discovery to the generic Linux cacheinfo subsystem.

## Important APIs, Types, And Functions
types `riscv_cacheinfo_ops`, `attribute_group`, `cacheinfo`, `cache_type`; functions/prototypes `riscv_set_cacheinfo_ops`; macros/constants `_ASM_RISCV_CACHEINFO_H`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `linux/cacheinfo.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 20 lines, 511 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheinfo.h -->
