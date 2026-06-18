<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative.h

## Purpose
Declares the RISC-V runtime alternatives patching interface used to rewrite boot, module, early-boot, vendor-errata, and CPU-feature instruction sequences.

## Important APIs, Types, And Functions
types `alt_entry`; functions/prototypes `apply_module_alternatives`, `riscv_alternative_fix_offsets`, `andes_errata_patch_func`, `mips_errata_patch_func`, `sifive_errata_patch_func`, `thead_errata_patch_func`, `riscv_cpufeature_patch_func`, `apply_boot_alternatives`, `apply_early_boot_alternatives`; macros/constants `__ASM_ALTERNATIVE_H`, `PATCH_ID_CPUFEATURE_ID(p) lower_16_bits(p)`, `PATCH_ID_CPUFEATURE_VALUE(p) upper_16_bits(p)`, `RISCV_ALTERNATIVES_BOOT`, `RISCV_ALTERNATIVES_MODULE`, `RISCV_ALTERNATIVES_EARLY_BOOT`, `__ALT_PTR(a, f) ((void *)&(a)->f + (a)->f)`, `ALT_OLD_PTR(a) __ALT_PTR(a, old_offset)`, `ALT_ALT_PTR(a) __ALT_PTR(a, alt_offset)`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm/alternative-macros.h`, `linux/init.h`, `linux/kernel.h`, `linux/types.h`, `linux/stddef.h`, `asm/hwcap.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 73 lines, 2536 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative.h -->
