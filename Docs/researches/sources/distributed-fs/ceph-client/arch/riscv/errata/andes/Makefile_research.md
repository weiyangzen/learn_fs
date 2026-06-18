<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/andes/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/andes/Makefile

## Purpose
Builds Andes RISC-V errata support.

## Important APIs, Types, And Functions
Sets `CFLAGS_errata.o := -mcmodel=medany` for early alternatives and always adds `errata.o` within the enabled Andes errata directory.

## Control Flow
Kbuild compiles the errata object with early-boot-safe code model when required.

## State And Persistence
State is build flags and object inclusion only.

## Dependencies And Integration Points
Depends on top-level errata Makefile gating and `CONFIG_RISCV_ALTERNATIVE_EARLY`.

## Risks And Edge Cases
Incorrect code model can break early patching before full relocation.

## Test Signals
Signals are successful builds with `CONFIG_ERRATA_ANDES` and early alternatives enabled.

Source read size: 5 lines, 97 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/andes/Makefile -->
