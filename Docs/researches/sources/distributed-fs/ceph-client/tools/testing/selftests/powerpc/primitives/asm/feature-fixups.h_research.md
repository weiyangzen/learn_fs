# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/feature-fixups.h

## Purpose
`feature-fixups.h` is a copied powerpc header that describes feature-fixup section entry formats and assembler macros for alternative instruction patching. In this selftest tree it mainly supports headers that expect these macros to exist.

## Important APIs, Types, and Functions
Important macros include `FTR_ENTRY_LONG`, `FTR_ENTRY_OFFSET`, `START_FTR_SECTION`, `FTR_SECTION_ELSE_NESTED`, `MAKE_FTR_SECTION_ENTRY`, `BEGIN_FTR_SECTION`, `END_FTR_SECTION`, and related CPU/MMU/firmware feature section helpers. It also declares kernel-side fixup functions when built in kernel context.

## Control Flow and State
In userspace selftests the macros are compile/assembly-time constructs. They can emit section metadata but do not run patching code in the test process. State is encoded in ELF sections if a macro is used.

## Dependencies and Integration Points
It is included by `ppc_asm.h` and keeps copied assembly macros close to kernel form while building outside the kernel.

## Risks and Test Signals
Risks are macro drift from the kernel copy, accidental emission of unresolved kernel symbols, and alternative-section size mismatches. Test signals are clean assembly/preprocessing of primitive and ptrace assembly helpers.
