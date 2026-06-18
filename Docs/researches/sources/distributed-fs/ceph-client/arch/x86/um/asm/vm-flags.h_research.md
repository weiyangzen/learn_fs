<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/vm-flags.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/vm-flags.h

## Purpose
`vm-flags.h` sets UML/x86 default VMA flags for data and stack mappings.

## Important APIs, types, and functions
It defines `VMA_DATA_DEFAULT_FLAGS` on 32-bit and `VMA_STACK_DEFAULT_FLAGS` on 64-bit.

## Control flow
MM code includes these defaults while creating VMAs, selecting executable data on 32-bit and executable grow-down stacks on 64-bit.

## State and persistence behavior
No state exists.

## Dependencies and integration points
It depends on generic VMA flag macros.

## Risks and edge cases
Defaults affect executable memory policy and compatibility; tightening flags can break old UML userspace expectations.

## Test signals
Signals are ELF loading, stack execution compatibility tests, and memory permission checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/vm-flags.h -->
