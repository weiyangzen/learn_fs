# sources/distributed-fs/eos/namespace/ns_quarkdb/ContainerMD.cc

Purpose: implements `QuarkContainerMD`, the protobuf-backed directory/container metadata object for the QuarkDB namespace.

Important APIs/types/functions: constructors initialize ids, default mode, dense hash map sentinels, service pointers, flusher keys, and clocks. Major methods include `setServices`, `clone`, `InheritChildren`, `findItem`, `addContainer`, `removeContainer`, `addFile`, `removeFile`, permission `access`, name/time/tree/xattr mutators, `serialize`, `deserialize`, `loadChildren`, `initialize`, `initializeWithoutChildren`, `getEnv`, `copyContainerMap`, and `copyFileMap`.

Control flow: child lookup checks local child-name maps under read lock, then asynchronously asks file/container services for resolved ids. Add/remove operations validate empty names and name conflicts across file and container maps, mutate in-memory maps, write hash updates through `MetadataFlusher`, and notify file listeners with tree counter deltas. Serialization writes aligned protobuf bytes plus CRC32C and raw object size; deserialization delegates checksum parsing to `Serialization` then reloads child maps from QuarkDB through `MetadataFetcher`.

State and persistence: primary state is `ContainerMdProto mCont`, lazy `FutureWrapper` maps of files and subcontainers, qclient/flusher service pointers, derived QuarkDB child-map keys, and a high-resolution `mClock`. Persistent state lives in protobuf metadata plus per-container hash maps keyed by id suffixes.

Dependencies and integration: depends on file/container metadata services, `MetadataFlusher`, `MetadataFetcher`, `Serialization`, `PermissionHandler`, `DataHelper` CRC helpers, protobuf, qclient, and listener events. It is created by `QuarkContainerMDSvc` and used by hierarchical views/accounting.

Risks: child map and protobuf parent/name state must remain synchronized with services. `getName` returns a const reference into the protobuf protected by a lock only during access, so callers must not assume long-lived thread safety. Add/remove listener events use `location` as a container id hack. Copy constructor copies service pointers and maps keys but not child maps. Time fields are stored as raw `timespec` bytes, tying persisted representation to layout assumptions.

Test signals: `MetadataTests.cc` covers file/container serialization/deserialization; `VariousTests.cc` covers etag/env formatting through `FRIEND_TEST`; hierarchical tests exercise add/remove and tree behavior.
