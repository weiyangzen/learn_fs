# File Research: sources/block-storage/kvdo/vdo/packer.h

## Purpose
Declares compressed block packer structures and APIs.

## Key Structures
- `struct packer_bin`: list node, slot count, free space, flexible `incoming` VIO array.
- `struct packer`: callback thread id, bin count, usable compressed block size, max slots, sorted bin list, canceled bin, flush generation, admin state, and packer statistics.

## API Surface
Construction/destruction, compressibility test, stats snapshot, packing attempt, flush, lock-holder removal, flush generation increment, drain/resume, and dump functions.

## Integration Notes
The header documents packer batching semantics in detail: the first uncanceled VIO becomes the write agent, other fragments are packed into its block, and the agent shares its PBN lock with the clients after successful write.
