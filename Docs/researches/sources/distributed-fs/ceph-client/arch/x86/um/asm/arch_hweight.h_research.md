<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/arch_hweight.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/arch_hweight.h

## Purpose
`arch_hweight.h` routes UML hweight operations to the generic bitops implementation.

## Important APIs, types, and functions
It includes `<asm-generic/bitops/arch_hweight.h>` and exports no local code.

## Control flow
All calls compile to generic helpers selected by the included header.

## State and persistence behavior
No state is stored.

## Dependencies and integration points
It depends on generic bitops and `GENERIC_HWEIGHT` Kconfig selection.

## Risks and edge cases
The risk is performance rather than correctness if UML could use a better host intrinsic but does not.

## Test signals
Signals are bitops selftests/build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/arch_hweight.h -->
