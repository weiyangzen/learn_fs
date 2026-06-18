<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/patch-kernel -->
# sources/distributed-fs/ceph-client/scripts/patch-kernel

## Purpose

`patch-kernel` incrementally applies kernel version patches from a patch directory to a source tree until a requested stop version or until no next patch is found. It is legacy release-management automation for patching kernel tarball trees.

## Important APIs, Types, and Functions

The script parses source directory, patch directory, stop version, and optional `-ac` patch series arguments. It reads top-level `Makefile` version variables and searches for patch files in multiple compression formats.

## Control Flow

It determines the current kernel version, decides the next patch level, locates the matching patch file, decompresses when needed, applies it with `patch -p1 -s` from the source tree, checks for `.rej` files, removes `.orig` files on success, updates version state, and repeats until the stop condition.

## State and Persistence Behavior

It persistently mutates the kernel source tree by applying patches and deleting backup files. Reject files remain on failure for manual inspection.

## Dependencies and Integration Points

It depends on shell, patch, decompression tools for gzip/bzip/bzip2/zip/compress/plaintext patches, find, and the kernel top-level Makefile version scheme.

## Risks and Edge Cases

It assumes historical version naming and patch layout. Applying patches to a dirty tree can mix local changes with release patches. Reject detection is post-hoc, and compressed patch selection can choose unexpected files. Modern git workflows generally supersede it.

## Test Signals

Run on disposable source trees for one-step, multi-step, exact stop version, already-at-target, missing patch, compressed patch, and reject scenarios. Verify version variables and absence/presence of `.rej`/`.orig` files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/patch-kernel -->
