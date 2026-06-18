<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strlen.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strlen.S

## Purpose
`strlen.S` implements RISC-V string length with scalar and optional Zbb word-at-a-time variants.

## Important APIs, Types, And Functions
`strlen` is exported and aliased as `__pi_strlen`. The Zbb path uses `orc.b`, `not`, and `ctz`/`clz` to find the first NUL byte in a word.

## Control Flow
The scalar path increments a pointer until it reads NUL, then subtracts the original pointer. The Zbb path aligns down, masks irrelevant first-word bytes by shifting, scans word chunks for a NUL indicator, and adds byte offsets to produce the length.

## State And Persistence
No state is retained; it reads a NUL-terminated string.

## Dependencies And Integration Points
It depends on alternatives, Zbb support, endian-specific bit scan direction, and kernel string API callers.

## Risks
The first unaligned word handling intentionally reads before the string's start at the aligned word; this assumes the access is valid in kernel contexts. Endian shifts and count calculations are subtle.

## Test Signals
String tests across all alignments, empty strings, page-boundary cases, Zbb/non-Zbb builds, and early boot users are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strlen.S -->
