<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpu_type.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpu_type.h

## Purpose
This header declares SPARC CPU type identifiers and CPU implementation state.

## Important APIs, Types, and Functions
It defines enums/macros for CPU families and exposes variables/functions used to identify the running processor implementation.

## Control Flow
Early CPU probing sets the active CPU type; later code branches on it for cache, TLB, workaround, and platform behavior.

## State and Persistence Behavior
Detected CPU type is persistent global boot state. The header only declares the contract.

## Dependencies and Integration Points
It integrates CPU probing with cache/MMU, traps, performance, and errata workarounds.

## Risks
Misclassification selects wrong low-level routines and can destabilize the kernel.

## Test Signals
Boot representative SPARC CPU families and verify detected type in logs and selected fixup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cpu_type.h -->
