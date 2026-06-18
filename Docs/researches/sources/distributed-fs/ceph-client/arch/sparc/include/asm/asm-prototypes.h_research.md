<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm-prototypes.h

## Purpose
This header declares C prototypes used by SPARC assembly and kallsyms/modversion tooling.

## Important APIs, Types, and Functions
It includes prototypes for low-level routines referenced from assembly, including checksum, memory/string, user access, and trap/interrupt helper surfaces as configured.

## Control Flow
The compiler includes it while building assembly prototype metadata, allowing symbol type checking and modversion generation for assembly-visible functions.

## State and Persistence Behavior
There is no state; it is a compile-time contract file.

## Dependencies and Integration Points
It integrates SPARC assembly routines with C declarations and generic asm-prototypes infrastructure.

## Risks
Prototype drift causes link-time or runtime ABI bugs because assembly callers do not get normal C type checking.

## Test Signals
Build with `CONFIG_MODVERSIONS` and sparse/prototype warnings; verify no assembly symbol prototype mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/asm-prototypes.h -->
