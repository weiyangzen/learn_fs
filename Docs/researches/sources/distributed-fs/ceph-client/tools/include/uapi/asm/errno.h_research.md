# sources/distributed-fs/ceph-client/tools/include/uapi/asm/errno.h

## Purpose
Routes errno definitions to architecture-specific UAPI headers where Linux errno numbering differs, with generic errno as the default.

## Important APIs, Types, and Functions
Branches for x86, powerpc, sparc, alpha, mips, and hppa/parisc, including the matching arch errno header; otherwise includes `<asm-generic/errno.h>`.

## Control Flow, State, and Persistence
Preprocessor routing only. No runtime state.

## Dependencies and Integration
Depends on compiler architecture macros and relative source-tree arch headers. It integrates with tools that need target Linux errno values rather than host libc values.

## Risks and Test Signals
Risks include cross-compilation selecting the build host arch, missing arch-specific mappings, and duplicate definitions with libc headers. Test signals include preprocessing under each supported arch macro and numeric checks for errno values known to differ by architecture.
