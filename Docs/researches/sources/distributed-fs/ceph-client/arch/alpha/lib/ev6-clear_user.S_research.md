# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-clear_user.S

## Purpose
EV6-optimized `__clear_user` that zeroes userspace memory with exception-table recovery. The source was read as part of `subset-b-000628` and contains 213 lines.

## Important APIs, Types, and Functions
Exports `__clear_user` for EV6 builds.

## Control Flow
Handles misaligned head/tail ranges, clears aligned blocks with EV6-friendly scheduling and write hints, and maintains the residual byte count in the return register after successful stores. Faulting accesses use exception-table entries to return bytes left.

## State and Persistence Behavior
Mutates user memory, returns residual count, and contributes exception-table metadata.

## Dependencies
Depends on EV6 scheduling behavior, Alpha uaccess exception macros, usercopy ABI, and Makefile EV6 selection.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Optimization increases risk around residual counts and masked stores. Every user memory access must have the right exception fixup. EV6-only code must not be linked for generic targets.

## Test Signals
Run usercopy clear tests on EV6 config for all alignments, page-faulting tails, and zero lengths; compare with generic helper behavior.
