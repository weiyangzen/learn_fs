<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/bitops.h

## Purpose
Implements architecture bit operations using Zbb bit-scan alternatives and AMO-based atomic bit manipulation.

## Important APIs, Types, And Functions
functions/prototypes `variable_fls`, `arch_test_and_set_bit`, `arch_test_and_clear_bit`, `arch_test_and_change_bit`, `arch_set_bit`, `arch_clear_bit`, `arch_change_bit`, `arch_test_and_set_bit_lock`, `arch_clear_bit_unlock`, `arch___clear_bit_unlock`, `arch_xor_unlock_is_negative_byte`; macros/constants `_ASM_RISCV_BITOPS_H`, `__HAVE_ARCH___FFS`, `__HAVE_ARCH___FLS`, `__HAVE_ARCH_FFS`, `__HAVE_ARCH_FLS`, `CTZW`, `CLZW`, `__ffs(word)`, `__fls(word)`, `ffs(x) (__builtin_constant_p(x) ? __builtin_ffs(x) : variable_ffs(x))`, `fls(x)`, `__AMO(op)`, `__test_and_op_bit_ord(op, mod, nr, addr, ord)`, `__op_bit_ord(op, mod, nr, addr, ord)`, plus 4 more.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `linux/compiler.h`, `asm/barrier.h`, `asm/bitsperlong.h`, `asm-generic/bitops/__ffs.h`, `asm-generic/bitops/__fls.h`, `asm-generic/bitops/ffs.h`, `asm-generic/bitops/fls.h`, `asm/alternative-macros.h`, `asm/hwcap.h`, `asm-generic/bitops/ffz.h`, plus 9 more. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 362 lines, 9926 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/bitops.h -->
