<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strnlen.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strnlen.S

## Purpose
`strnlen.S` implements bounded string length with scalar and optional Zbb word scanning.

## Important APIs, Types, And Functions
`strnlen` is exported and aliased as `__pi_strnlen`. It returns the smaller of the first NUL position and the supplied maximum.

## Control Flow
The scalar path advances until the end pointer or NUL. The Zbb path handles maxlen zero, scans the first unaligned word with masking, clamps by maxlen, then scans aligned words until NUL or boundary.

## State And Persistence
No state is stored; it reads bounded string memory.

## Dependencies And Integration Points
It uses RISC-V alternatives, Zbb instructions, endian-specific bit scans, and kernel string API integration.

## Risks
The Zbb path must clamp results and avoid unsafe reads around maxlen/page boundaries. Initial unaligned word handling is subtle.

## Test Signals
Tests should cover zero length, no NUL within bound, NUL at each alignment, Zbb vs scalar comparison, and page-boundary strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strnlen.S -->
