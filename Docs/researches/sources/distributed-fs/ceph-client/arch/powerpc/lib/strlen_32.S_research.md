<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/strlen_32.S -->
# sources/distributed-fs/ceph-client/arch/powerpc/lib/strlen_32.S

## Purpose
This PPC32 assembly file implements an optimized `strlen` using word-at-a-time zero-byte detection.

## Important APIs, types, and functions
It exports `_GLOBAL(strlen)`. Constants loaded into registers implement low magic `0x01010101` and high magic `0x80808080`; `cntlzw` identifies the first matching zero byte.

## Control flow
The function aligns back to a word boundary, masks any bytes before the original string as non-zero for misaligned inputs, loops over words until the zero-byte test fires, then computes the byte index of the first NUL and returns the distance from the original pointer.

## State and persistence behavior
No memory is modified. All state is transient in registers.

## Dependencies and integration points
This is the PPC32 kernel `strlen` primitive exported for string users. It depends on valid readable kernel string memory and PPC32 endian-sensitive word layout.

## Risks and edge cases
The algorithm has different least-zero-byte concerns on big-endian versus little-endian systems; the comments document a second test to identify the correct byte. Misaligned input handling must not falsely see bytes before the string as NUL.

## Test signals
Generic kernel string tests, boot-time string operations, and architecture self-tests provide coverage; no local test file accompanies it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/lib/strlen_32.S -->
