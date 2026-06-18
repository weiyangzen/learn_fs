# sources/distributed-fs/openafs/src/rx/xdr_arrayn.c

## Purpose
`xdr_arrayn.c` provides `xdr_arrayN`, a kernel-only variant of counted array marshalling.

## Important APIs, Types, and Functions
- `xdr_arrayN()` mirrors `xdr_array()` but is compiled under `#ifdef KERNEL`.

## Control Flow
It follows the same count-read/write, maximum validation, optional decode allocation, per-element loop, and free behavior as `xdr_array.c`.

## State and Persistence
Decoded storage is allocated via `osi_alloc` and freed through `osi_free`. `*sizep` is updated to the wire count after successful capacity validation.

## Dependencies and Integration Points
Integrated into kernel XDR consumers and declared in `xdr_prototypes.h`. Includes kernel-specific headers and OpenBSD allocation compatibility glue.

## Risks and Edge Cases
The implementation is largely duplicated from `xdr_array`; divergence between the two can create user/kernel behavior differences. Like `xdr_array`, `elsize == 0` would be invalid.

## Test Signals
Kernel build coverage and array round-trip tests should match `xdr_array` semantics, including oversized and preallocated-buffer rejection.
