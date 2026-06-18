<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/required-features.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/required-features.h

## Purpose
`required-features.h` is a placeholder needed by shared x86 headers when building UML, where native boot CPU feature enforcement is not used.

## Important APIs, types, and functions
It exports only include guards and no runtime functions or types.

## Control flow
Compilation includes the shim to satisfy generic header dependencies; no control flow is generated.

## State and persistence behavior
No runtime or persistent state exists.

## Dependencies and integration points
It depends on include ordering in the UML/x86 header stack.

## Risks and edge cases
Adding native hardware assumptions here would be incorrect for UML and could pull in unavailable definitions.

## Test signals
Signals are successful UML builds that include generic x86 headers without unresolved APIC/vector/feature dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/required-features.h -->
