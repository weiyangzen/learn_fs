<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_64.h

## Purpose
`checksum_64.h` adds 64-bit UML checksum glue.

## Important APIs, types, and functions
It defines `add32_with_carry()` and declares `ip_compute_csum()`.

## Control flow
The inline helper performs a 32-bit add and folds carry with `adcl`; full checksum work is provided by linked 64-bit library code.

## State and persistence behavior
No persistent state exists.

## Dependencies and integration points
It depends on x86-64 checksum library objects selected by `um/Makefile`.

## Risks and edge cases
Assembly constraints must maintain 32-bit semantics on 64-bit registers.

## Test signals
Signals are 64-bit UML networking checksum tests and successful linking of `ip_compute_csum`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/checksum_64.h -->
