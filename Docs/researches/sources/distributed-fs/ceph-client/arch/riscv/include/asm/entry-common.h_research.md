<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/entry-common.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/entry-common.h

## Purpose
Declares C entry points reached from low-level exception, page-fault, breakpoint, misaligned-access, vector, and CFI paths.

## Important APIs, Types, And Functions
types `pt_regs`; functions/prototypes `arch_exit_to_user_mode_prepare`, `handle_page_fault`, `handle_break`, `handle_misaligned_load`, `handle_misaligned_store`, `handle_user_cfi_violation`; macros/constants `_ASM_RISCV_ENTRY_COMMON_H`, `arch_exit_to_user_mode_prepare`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm/stacktrace.h`, `asm/thread_info.h`, `asm/vector.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 45 lines, 1119 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/entry-common.h -->
