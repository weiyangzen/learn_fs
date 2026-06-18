# sources/distributed-fs/openafs/src/WINNT/afsd/cm_rdr.h

## Purpose
`cm_rdr.h` is a bridge header between the user-mode Windows cache manager and the AFS redirector interface. It centralizes inclusion of redirector user definitions, structures, and prototypes.

## Important APIs and types
The file does not define new APIs. It includes:
- `..\afsrdr\common\AFSUserDefines.h`
- `..\afsrdr\common\AFSUserStructs.h`
- `..\afsrdr\common\AFSUserPrototypes.h`

## Control flow and state behavior
There is no executable code or state. The header only controls visibility of redirector contracts to cache-manager code.

## Dependencies and integration points
It depends on the Windows redirector common headers. Modules such as `cm_scache.c` integrate with redirector invalidation and buffer ownership (`RDR_InvalidateObject`, redirector cache state, and request-source flags) through these shared definitions.

## Risks and edge cases
- The relative include paths are Windows-build-specific and can be fragile for non-standard build roots.
- This header hides a large external contract behind a small wrapper; changes in the redirector common headers can affect cache-manager modules without local changes here.

## Test signals
Primary signals are build and ABI compatibility tests: user-mode afsd must compile against the redirector common headers, and redirector invalidation/request structures must remain binary-compatible with kernel-side consumers.
