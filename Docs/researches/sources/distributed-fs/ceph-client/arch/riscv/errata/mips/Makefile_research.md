<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/mips/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/mips/Makefile

## Purpose
Builds MIPS RISC-V errata support.

## Important APIs, Types, And Functions
Sets early-alternative `CFLAGS_errata.o := -mcmodel=medany` and includes `errata.o`.

## Control Flow
Kbuild compiles the MIPS errata object when the top-level errata directory selects it.

## State And Persistence
State is build graph and flags only.

## Dependencies And Integration Points
Depends on `CONFIG_ERRATA_MIPS` and early alternatives config.

## Risks And Edge Cases
Wrong early code model can break pre-relocation errata code.

## Test Signals
Signals are builds with MIPS errata enabled and object inclusion in vmlinux/modules.

Source read size: 5 lines, 97 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/mips/Makefile -->
