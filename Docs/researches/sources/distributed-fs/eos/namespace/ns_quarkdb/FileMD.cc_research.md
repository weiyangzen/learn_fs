# sources/distributed-fs/eos/namespace/ns_quarkdb/FileMD.cc

Purpose: implements `QuarkFileMD`, the protobuf-backed file metadata object for the QuarkDB namespace.

Important APIs/types/functions: constructors, copy/assignment, `clone`, `setName`, location lifecycle methods (`addLocation`, `unlinkLocation`, `removeLocation`, bulk variants), `getEnv`, `serialize`, `initialize`, `deserialize`, `getProto`, `setSize`, time getters/setters, xattr map copy, unlinked-location checks, and alternate checksum methods.

Control flow: mutations use `runWriteOp`; reads use `runReadOp`. Location add/unlink/remove update repeated protobuf fields and notify file service listeners with `LocationAdded`, `LocationUnlinked`, or `LocationRemoved`. `setSize` masks size to 48 bits, computes signed delta, and emits `SizeChange`. Serialization mirrors container serialization with aligned protobuf bytes and CRC32C. `setMTimeNow` resets sync time to zero so sync time falls back to mtime.

State and persistence: primary state is `FileMdProto mFile`, service pointer, and `mClock`. Persistent state is serialized protobuf with checksum/size envelope. Locations, unlinked locations, checksums, xattrs, symlink target, layout, flags, ownership, and times are stored in the protobuf.

Dependencies and integration: depends on `QuarkFileMDSvc`, `Serialization`, `DataHelper`, checksum/string conversion helpers, protobuf, and file change listeners. Files are managed by `QuarkFileMDSvc`, referenced by containers, filesystem view, quota/accounting, and inspector tools.

Risks: assignment copies protobuf and clock but resets `pFileMDSvc` to null, so copied objects cannot notify unless service is reset. Location unlink emits an event even if the location was not found. `getProto` returns a reference without locking for the caller lifetime. Time fields are raw byte copies. `setSize` truncates to 48 bits by design but can surprise callers.

Test signals: `MetadataTests.cc` covers serialization/deserialization; `VariousTests.cc` covers etag/env formatting and alternate checksum behavior; filesystem/accounting tests exercise location and size listener paths.
