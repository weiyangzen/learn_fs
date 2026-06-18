# sources/cloud-native/composefs/tests/test-random-fuse.sh

## Purpose
This shell test generates random filesystem trees, builds composefs images, verifies dump reproducibility, and when possible checks FUSE-mounted views against source dumps.

## Important APIs, Types, And Functions
Main function `test_random` uses `gendir`, `dumpdir`, `mkcomposefs`, optional `fsck.erofs`, `composefs-dump`, `composefs-info dump`, `composefs-fuse`, and diff/cmp checks.

## Control Flow
It creates a temp workdir, sources `test-lib.sh`, configures generator flags based on whiteout support and optional `seed`, then runs once with a seed or ten times without. Each iteration generates a root, dumps it, builds an image/object store, checks reproducibility, optionally mounts through FUSE twice, and compares dumps.

## State And Persistence
All state is under a temporary workdir removed on exit. It creates and unmounts FUSE mounts.

## Dependencies And Integration Points
Depends on built tools, Python helpers, optional FUSE capability, optional fsck, and valgrind prefix support.

## Risks
Random coverage can be flaky if host filesystem semantics vary. FUSE paths depend on privileges and `/dev/fuse`. Generated seeds should be retained from logs for reproduction.

## Test Signals
Broad stress coverage for tree ingestion, inline/object split, xattrs, whiteouts, symlinks, special files, image dump/load, and FUSE behavior.
