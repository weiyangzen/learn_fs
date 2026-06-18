<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_notify_test.go

## Purpose
Tests protobuf marshal/unmarshal preservation for metadata event notifications containing chunk metadata.

## Important APIs and Functions
`TestProtoMarshal` builds an `Entry`, converts it to protobuf, embeds it in `filer_pb.EventNotification`, marshals and unmarshals it, and checks `SourceFileId`.

## Control Flow and State
The test has only in-memory protobuf state. It prints the marshaled bytes after validating the important field.

## Persistence Behavior
No persistence. It protects serialized notification payload shape used by log buffers and external notifications.

## Dependencies and Integration Points
Uses `proto.Marshal`, `filer_pb.EventNotification`, `Entry.ToProtoEntry`, and chunk metadata fields used by filer sync.

## Risks
Only one field is asserted. The print statement is noisy in test output. It does not cover full `SubscribeMetadataResponse`, signatures, delete flags, or event replay.

## Test Signals
Narrow but useful signal that `SourceFileId` survives notification serialization, important for cross-cluster chunk delta logic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_notify_test.go -->
