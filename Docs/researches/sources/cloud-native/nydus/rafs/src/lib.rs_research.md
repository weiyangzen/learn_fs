<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/lib.rs -->
# sources/cloud-native/nydus/rafs/src/lib.rs

## Purpose

This crate root documents RAFS, declares public modules, defines crate-wide error/result types, abstracts bootstrap IO readers/writers, and provides an iterator over RAFS inode trees.

## Important APIs, Types, and Functions

Public modules include `blobfs` behind `virtio-fs`, `fs`, `metadata`, test-only `mock`, and `prefetch`. `RafsError` enumerates RAFS failure modes. `MetaType` classifies metadata errors. `RafsIoRead` and `RafsIoWrite` abstract file-like bootstrap IO, with helpers for alignment, padding, seeking, finalization, and byte extraction. `RafsIterator` walks all inodes depth-first.

## Control Flow

Reader/writer helpers wrap seek/write operations with Nydus errors and logging. `RafsIterator::new` starts from the root inode if available; `next` pops a node and pushes directory children in reverse order so iteration yields natural forward order.

## State and Persistence Behavior

The crate root itself maintains no global state. IO traits operate on supplied files/buffers, and iterator state is an in-memory stack of inode/path pairs.

## Dependencies and Integration Points

It brings in logging, bitflags, nydus-api, and nydus-storage macros. It exposes types consumed by metadata loading, RAFS building, and tests throughout the crate.

## Risks and Test Signals

`RafsIoWrite::as_bytes` is unimplemented by default and must be overridden by in-memory writers. Alignment helpers assume power-of-two alignment. Tests cover writer alignment/padding/seek helpers and iterator traversal over a fixture bootstrap.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/lib.rs -->
