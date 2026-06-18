# sources/distributed-fs/seaweedfs/weed/filer/entry_codec.go

## Purpose
This file implements efficient serialization/deserialization of filer entries to protobuf bytes and conversion between `Entry.Attr` and protobuf `FuseAttributes`.

## Important APIs, Types, and Functions
- `pbEntryPool` reuses `filer_pb.Entry` objects with preallocated attributes.
- `resetPbEntry` and `resetFuseAttributes` clear pooled protobuf objects before reuse.
- `EncodeAttributesAndChunks` marshals an entry to bytes.
- `DecodeAttributesAndChunks` unmarshals bytes into an existing entry.
- Attribute conversions: `EntryAttributeToPb`, `EntryAttributeToExistingPb`, `PbToEntryAttribute`, `atimeSecondsForPb`, and `atimeNanosForPb`.
- Equality helpers: `EqualEntry` and `eq`.

## Control Flow and State
Encoding gets a pooled protobuf entry, fills it through `ToExistingProtoEntry`, marshals it, copies the returned bytes to avoid retaining mutable pooled memory, resets the message, and returns it to the pool. Decoding gets a pooled message, unmarshals into it, copies fields into the target entry, resets, and returns it. Attribute conversion preserves nanoseconds for mtime, ctime, and atime; missing ctime falls back to mtime and missing atime falls back to mtime.

## State and Persistence Behavior
The protobuf bytes produced here are the metadata blobs persisted by filer stores. The fallback behavior for ctime/atime preserves compatibility with older blobs that lack those fields.

## Dependencies and Integration Points
It uses `google.golang.org/protobuf/proto`, `filer_pb.Entry`, `filer_pb.FuseAttributes`, and conversion helpers in `entry.go`. All filer stores call these methods before storing and after loading metadata.

## Risks and Edge Cases
- Pool reuse requires complete reset; missed fields could leak between entries.
- The marshaled data copy is intentional and should not be removed without proving protobuf marshal ownership.
- `EqualEntry` compares protobuf-converted attributes and selected entry fields, but not every field from `Entry` such as full path.
- Atime zero semantics distinguish all-zero missing atime from sub-second epoch atime using `AtimeNs`.

## Test Signals
`entry_codec_atime_test.go` verifies atime round trip, fallback to mtime, and sub-second epoch preservation. More tests should cover pool reset isolation and equality behavior.
