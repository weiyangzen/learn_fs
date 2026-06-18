# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/FSWrapper.java

## Purpose
`FSWrapper` defines a common interface for filesystem operations used by generic tests, effectively extracting a `FileContext`-like API that can be implemented over multiple Hadoop filesystem abstractions.

## Important APIs, Types, and Functions
The interface declares working-directory methods, path qualification, create, mkdir, delete, open, replication, rename, permission/owner/time mutation, checksum lookup, file and link status, symlink target, block locations, symlink creation, status iteration, listing, and globbing. It uses `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `FileChecksum`, `BlockLocation`, `RemoteIterator`, `PathFilter`, `Options.CreateOpts`, and `Options.Rename`.

## Control Flow
There is no implementation control flow in this file. It defines the operations that concrete wrappers must route to `FileSystem` or `FileContext`.

## State and Persistence
The interface owns no state. State and persistence are entirely in implementing wrappers and their backing filesystems.

## Dependencies and Integration Points
Dependencies include Hadoop path, permission, checksum, symlink, block-location, and stream types plus security exceptions. It is an integration seam for shared filesystem contract tests.

## Risks and Edge Cases
Because it abstracts two similar but not identical APIs, implementers must preserve exception types, symlink semantics, recursive delete behavior, create flags, rename options, and status/link-status distinctions.

## Test Signals
Any generic test written against `FSWrapper` can validate a concrete wrapper's conformance across creation, mutation, metadata, links, block locations, listing, and globbing.
