# sources/cloud-native/composefs/tests/dumpdir

## Purpose
`dumpdir` is a Python test utility that prints a deterministic textual dump of a filesystem tree, including metadata, content digest, symlink target, and xattrs. It is used to compare source directories, mounted composefs views, and FUSE views.

## Important APIs, Types, And Functions
Core functions are `should_convert_whiteout`, `has_whiteout_child`, `dumpfile`, and `dumpdir`. CLI options control nlink normalization, user xattrs only, whiteout conversion, and escaped-overlay xattr filtering.

## Control Flow
The script dumps the root then walks directories top-down with sorted dirs and files. For each path it uses `lstat`, optionally converts whiteout chardevs to overlay-style regular-file markers, prints stat fields, regular-file SHA-256 or symlink target, then sorted xattrs.

## State And Persistence
It reads filesystem state but does not modify it. Output is a stable comparison artifact.

## Dependencies And Integration Points
Used by `integration.sh` and `test-random-fuse.sh`. Depends on Python `os`, `stat`, `hashlib`, `shlex`, and xattr support.

## Risks
Requires permissions to read files and xattrs. Whiteout conversion depends on test flags and kernel/device permissions. Full file reads can be expensive for large trees.

## Test Signals
This utility is itself a test oracle for mount/FUSE equivalence and random-tree round trips.
