<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/Makefile

## Purpose
Builds SiFive errata support and the optional CIP-453 trap shim.

## Important APIs, Types, And Functions
Adds `errata_cip_453.o` when `CONFIG_ERRATA_SIFIVE_CIP_453` is enabled and always includes `errata.o`.

## Control Flow
Kbuild links the generic SiFive errata probe/patch code and optional assembly trap handlers.

## State And Persistence
State is object inclusion only.

## Dependencies And Integration Points
Depends on SiFive errata Kconfig symbols and alternative users that reference CIP-453 handlers.

## Risks And Edge Cases
Omitting `errata_cip_453.o` while alternatives reference its symbols would produce link errors.

## Test Signals
Signals are builds with CIP-453 enabled/disabled and symbol resolution for trap replacement handlers.

Source read size: 2 lines, 74 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/sifive/Makefile -->
