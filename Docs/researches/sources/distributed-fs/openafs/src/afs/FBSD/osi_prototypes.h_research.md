# sources/distributed-fs/openafs/src/afs/FBSD/osi_prototypes.h

## Purpose
Declares FreeBSD-specific OSI helper routines used outside their implementation files.

## Important APIs, Types, And Functions
Declares `osi_lookupname`, `osi_fbsd_alloc`, `osi_fbsd_free`, and `osi_fbsd_checkinuse`.

## Control Flow
There is no executable flow.

## State And Persistence
No state is declared directly; prototypes expose helpers that interact with vnode, allocation, and vcache state.

## Dependencies And Integration Points
Depends on FreeBSD `uio_seg`, `vnode`, `size_t`, and OpenAFS `vcache` types. Included by generic/platform code requiring these helpers.

## Risks
Prototype mismatch would break path lookup, memory allocation, or vcache eviction integration.

## Test Signals
FreeBSD builds with warnings enabled should show no implicit declarations or incompatible pointer warnings for these helpers.
