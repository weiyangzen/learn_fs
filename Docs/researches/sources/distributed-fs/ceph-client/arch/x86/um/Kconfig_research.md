<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/Kconfig -->
# sources/distributed-fs/ceph-client/arch/x86/um/Kconfig

## Purpose
`um/Kconfig` selects x86 UML architecture capabilities and 32-bit versus 64-bit UML configuration.

## Important APIs, types, and functions
Important symbols are `UML_X86`, `64BIT`, `X86_32`, `X86_64`, `ARCH_HAS_SC_SIGNALS`, and `GENERIC_HWEIGHT`; it also sources `arch/x86/Kconfig.cpu`.

## Control flow
Kconfig derives bitness from `SUBARCH`, selects module ELF relocation style, old syscall ABI flags for 32-bit, queued locks, efficient unaligned access, and SMP support when `X86_CX8` exists.

## State and persistence behavior
State is compile-time configuration only.

## Dependencies and integration points
It depends on Kconfig CPU feature definitions and UML generic architecture configuration.

## Risks and edge cases
Wrong defaults can build a UML binary for the wrong host ABI or select incompatible syscall/module semantics.

## Test signals
Signals are `allnoconfig`/`defconfig` UML builds for i386 and x86_64 and inspection of selected module relocation formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/Kconfig -->
