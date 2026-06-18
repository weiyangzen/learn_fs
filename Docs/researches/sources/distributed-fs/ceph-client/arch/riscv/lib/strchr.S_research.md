<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strchr.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strchr.S

## Purpose
`strchr.S` implements bytewise search for the first occurrence of a character in a NUL-terminated string.

## Important APIs, Types, And Functions
The exported `strchr` symbol masks the search character to 8 bits and returns either the matching address or zero. `__pi_strchr` aliases it for position-independent early code.

## Control Flow
The loop loads one unsigned byte, compares it with the target, advances on mismatch, and stops with NULL if the NUL terminator is reached first.

## State And Persistence
No state is stored; it reads the input string.

## Dependencies And Integration Points
It is a core string helper used throughout the kernel when generic/KASAN string replacements are not selected.

## Risks
The function assumes a valid NUL-terminated string. It must match C semantics where searching for `\0` returns the terminator address.

## Test Signals
lib/string tests covering target present, absent, and NUL target validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strchr.S -->
