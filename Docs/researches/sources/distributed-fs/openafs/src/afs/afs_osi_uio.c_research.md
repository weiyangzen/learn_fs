# sources/distributed-fs/openafs/src/afs/afs_osi_uio.c

## Purpose
`afs_osi_uio.c` provides portable helper routines for copying, trimming, partially copying, freeing, and advancing `struct uio` objects used by AFS read/write paths.

## Important APIs, types, and functions
For non-Darwin80 builds, `afsio_copy` copies a uio and its iovec array into caller-provided storage, `afsio_trim` clamps a uio to a target byte size, `afsio_partialcopy` allocates a small-space block containing a copied uio and up to `AFS_MAXIOVCNT` iovecs, and `afsio_free` frees that allocation. `afsio_skip` advances an existing uio by a byte count and is available for all builds, using `uio_update` on Darwin80.

## Control flow
`afsio_copy` rejects iovec counts above `AFS_MAXIOVCNT`, shallow-copies the uio structure, redirects the output uio to the output iovec array, and copies each input iovec. `afsio_trim` sets resid to the target size and walks iovecs until the target is covered, truncating the final iovec or shortening the iovec count. `afsio_partialcopy` allocates a combined uio/iovec buffer, zeroes it, copies the source uio, trims it, and returns the new uio. `afsio_skip` repeatedly advances the current iovec base/length, resid, and offset until the skip count is consumed or the uio is empty.

## State and persistence behavior
There is no persistent state. The helpers mutate supplied uio structures or allocate transient small-space copies.

## Dependencies and integration points
The file depends on OSI small-space allocation, `AFS_MAXIOVCNT`, platform uio field aliases from headers, and AFS stats. It is used by cache read/write paths that need to split or advance user IO without losing the original vector.

## Risks and edge cases
Multiple-iovec behavior is noted as not thoroughly tested in comments. `afsio_partialcopy` assumes small-space blocks are large enough for one uio plus `AFS_MAXIOVCNT` iovecs. `afsio_skip` silently stops when resid reaches zero and skips zero-length iovecs by advancing the vector pointer.

## Test signals
Test copying at max and over-max iovec counts, trimming exact/partial/zero lengths, partialcopy allocation layout, skip across empty and multiple iovecs, offset/resid consistency, and Darwin80 `uio_update` behavior.
