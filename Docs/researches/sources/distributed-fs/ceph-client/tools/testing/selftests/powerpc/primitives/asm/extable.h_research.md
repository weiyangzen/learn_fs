# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/extable.h

## Purpose
`extable.h` supplies the relative exception-table macros used by the userspace `load_unaligned_zeropad` test to emulate kernel-style fault fixups.

## Important APIs, Types, and Functions
It defines `ARCH_HAS_RELATIVE_EXTABLE` and macros such as `EX_TABLE(_fault, _target)` that emit relative instruction/fixup entries into the `__ex_table` section.

## Control Flow and State
No C runtime flow exists in the header. At assembly time, faulting instruction and fixup label offsets are emitted; at runtime the test's SIGSEGV handler walks these entries and redirects NIA to the fixup target.

## Dependencies and Integration Points
It is included by `word-at-a-time.h` and consumed by `load_unaligned_zeropad.c` through linker-provided `__start___ex_table` and `__stop___ex_table` symbols.

## Risks and Test Signals
Risks are malformed relative offsets, section-name mismatch, and linker behavior changes. A pass means the SIGSEGV handler finds entries and resumes execution at the expected fixup code.
