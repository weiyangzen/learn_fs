<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/thead/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/thead/Makefile

## Purpose
Builds T-Head errata support with early-boot-safe instrumentation restrictions.

## Important APIs, Types, And Functions
For early alternatives it sets `-mcmodel=medany`, removes ftrace flags from `errata.o`, disables KASAN instrumentation, and includes `errata.o`.

## Control Flow
Kbuild applies these flags before compiling the T-Head errata object.

## State And Persistence
State is build flags and object inclusion.

## Dependencies And Integration Points
Depends on RISC-V early alternatives, ftrace, KASAN, and top-level T-Head errata gating.

## Risks And Edge Cases
Early errata code must run before instrumentation and full relocation are safe; accidental ftrace/KASAN instrumentation can break boot.

## Test Signals
Signals are builds with early alternatives plus ftrace/KASAN enabled and no instrumentation in the errata object.

Source read size: 11 lines, 221 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/thead/Makefile -->
