# sources/distributed-fs/eos/proto/namespace/ns_quarkdb/FileMd.proto

## Purpose
Defines the QuarkDB protobuf representation of EOS file metadata. It is the durable wire schema for file identity, ownership, layout, checksums, locations, xattrs, and timestamps.

## Important APIs, types, and functions
`FileMdProto` includes `id`, parent container id, uid/gid, size, layout id, flags, binary name and link target, ctime/mtime/stime/atime byte fields, primary checksum, replica `locations`, `unlink_locations`, string-to-bytes xattrs, alternative checksums keyed by algorithm id, and transient clone fields 256/257.

## Control flow
There is no executable logic. Generated code supplies accessors and serialization for namespace services.

## State and persistence
Field numbering is storage compatibility. Locations and unlink locations encode replica lifecycle, while checksum and layout fields feed data-integrity and placement logic. Binary timestamp/name fields require length-safe handling.

## Dependencies and integration points
Package `eos.ns` integrates with QuarkDB namespace file metadata, fsck, FST reconciliation, conversion, recycle, and stat/listing code.

## Risks and test signals
Risks include incompatible schema changes, inconsistent location/unlink state, checksum length mismatch for layout, and transient clone leakage into durable decisions. Tests should round-trip all fields, decode legacy records, preserve map fields, and verify namespace code handles absent optional proto3 fields correctly.
