<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess.S

## Purpose
`uaccess.S` implements RISC-V assembly user-copy and clear-user primitives, including scalar fallback and optional vector dispatch.

## Important APIs, Types, And Functions
It exports `__asm_copy_to_user`, `__asm_copy_from_user`, `_sum_enabled` variants, `fallback_scalar_usercopy`, `fallback_scalar_usercopy_sum_enabled`, and `__clear_user`. The `fixup` macro emits exception table entries for fault recovery.

## Control Flow
Top-level copy wrappers enable SUM when needed, optionally dispatch to vector usercopy for large copies on vector-capable systems, then fall back to scalar copy. The scalar copy aligns destination, uses word copy or shift-copy for misaligned source, copies tail bytes, and returns remaining bytes on exception. `__clear_user` enables SUM, zeroes aligned words and edge bytes, and returns uncleared bytes on fault.

## State And Persistence
The routines mutate user/kernel memory and temporarily set/clear `SR_SUM`. No persistent state is stored.

## Dependencies And Integration Points
They depend on exception-table fixups, CSR_STATUS/SUM semantics, vector threshold helpers, RISC-V alternatives, and core `copy_{to,from}_user`/`clear_user` APIs.

## Risks
SUM must be cleared on all exit paths. Exception fixups must report exact remaining bytes. Vector dispatch must preserve fault semantics. Misaligned shift-copy is sensitive to page faults and endpoint calculations.

## Test Signals
Usercopy selftests, fault-injection on invalid user pages, KASAN/KMSAN builds, vector and non-vector systems, and hardened usercopy tests are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/uaccess.S -->
