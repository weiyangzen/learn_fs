# sources/distributed-fs/eos/proto/namespace/ns_quarkdb/ContainerMd.proto

## Purpose
Defines the QuarkDB protobuf representation of EOS container metadata. It is a persistent schema for directories in the namespace.

## Important APIs, types, and functions
`ContainerMdProto` includes ids, owner uid/gid, `tree_size`, `mode`, `flags`, binary `name`, binary ctime/mtime/stime fields, string-to-bytes xattrs, recursive tree counters for containers and files, plus high-number transient `cloneid` and `clonefst` fields.

## Control flow
No executable flow is present. Generated protobuf accessors are used by namespace storage and migration code.

## State and persistence
Fields 1-14 are durable metadata. The transient clone fields use ids 256 and 257, signaling a separate compatibility surface. Binary time fields imply callers serialize native or EOS-specific time structures into bytes.

## Dependencies and integration points
Package `eos.ns` integrates with QuarkDB namespace services, container metadata classes, views, and tools that inspect or migrate namespace records.

## Risks and test signals
Wire compatibility is the main risk. Tests should cover old-record decoding, xattr map preservation, binary name handling, tree counter consistency, mode/flag round trips, and clone field treatment as transient rather than authoritative persisted namespace state.
