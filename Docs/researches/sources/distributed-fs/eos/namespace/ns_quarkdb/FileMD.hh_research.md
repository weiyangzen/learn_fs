# sources/distributed-fs/eos/namespace/ns_quarkdb/FileMD.hh

Purpose: declares `QuarkFileMD`, the QuarkDB implementation of `IFileMD`.

Important APIs/types/functions: exposes id, container id, size, clone metadata, checksum, name, locations, unlinked locations, ownership, layout, flags, link, xattrs, serialization/deserialization, protobuf initialization/access, clock, and alternate checksum APIs. It also declares no-lock helper methods for times and location checks.

Control flow: inline methods wrap protobuf fields with `runReadOp`/`runWriteOp`. Non-inline methods handle validation, listener notification, serialization, and repeated-field manipulation.

State and persistence: declares `FileMdProto mFile`, `pFileMDSvc`, and `mClock`; all durable file metadata is in the protobuf.

Dependencies and integration: implements `IFileMD`, depends on `FileMDSvc.hh` for the Quark service type and `FileMd.pb.h` for storage schema. `FileSystemView` is a friend for direct access.

Risks: friend access and public `getProto` can bypass lock discipline. Default constructor leaves service null for tests/dumps. Some APIs return copies while others expose references through later implementation, so caller expectations need care.

Test signals: `FRIEND_TEST(VariousTests, EtagFormatting)` and metadata tests cover important formatting and serialization paths.
