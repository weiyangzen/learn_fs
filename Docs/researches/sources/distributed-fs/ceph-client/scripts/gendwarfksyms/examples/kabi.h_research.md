# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi.h

## Purpose
`examples/kabi.h` provides userspace-testable macros that emit `gendwarfksyms` kABI rules and demonstrate ABI-preserving structure evolution patterns.

## Important APIs, Types, and Functions
Rule macros emit strings into `.discard.gendwarfksyms.kabi_rules`: `KABI_DECLONLY`, `KABI_ENUMERATOR_IGNORE`, `KABI_ENUMERATOR_VALUE`, `KABI_BYTE_SIZE`, and `KABI_TYPE_STRING`. Layout macros include `KABI_RESERVE`, `KABI_RESERVE_ARRAY`, `KABI_IGNORE`, `KABI_REPLACE`, `KABI_USE`, `KABI_USE2`, and `KABI_USE_ARRAY`.

## Control Flow
The macros expand at compile time into static used section entries or unions with static assertions that replacement fields fit the reserved size/alignment.

## State and Persistence Behavior
The header contributes ELF section data consumed by `kabi.c`; it does not create runtime state in the tested program.

## Dependencies and Integration Points
It mirrors kernel-style kABI macro patterns and is included by `kabi_ex.h` examples.

## Risks and Test Signals
Correctness depends on developers preserving actual ABI compatibility; the macros can hide version changes but cannot prove semantic safety. Test by compiling example objects and checking emitted stable output with FileCheck.
