<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/errata/Makefile

## Purpose
Configures RISC-V vendor errata build flags and selects vendor errata subdirectories.

## Important APIs, Types, And Functions
Adds `-fno-pie -mcmodel=medany` for relocatable early errata parsing, disables fortify for early alternatives when needed, and includes andes, mips, sifive, and thead directories based on config symbols.

## Control Flow
Kbuild applies special flags before compiling early errata code, then descends into enabled vendor directories.

## State And Persistence
State is build configuration and compiler flags for errata objects.

## Dependencies And Integration Points
Integrated with RISC-V alternatives, relocatable kernel support, fortify, and vendor errata Kconfig symbols.

## Risks And Edge Cases
Early boot code cannot rely on GOT/PIE or fortified helpers. Wrong flags can break alternatives before relocation or instrumentation is ready.

## Test Signals
Signals are relocatable and early-alternative builds, plus vendor errata object inclusion only for enabled configs.

Source read size: 18 lines, 573 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/errata/Makefile -->
