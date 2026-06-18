# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/MetadataTests.cc

Purpose: Intended unit tests for file/container metadata serialization, deserialization, and checksum validation, but the actual tests are compiled out with `#if 0`.
Important APIs/types/functions: disabled tests use `MockFileMDSvc`, `MockContainerMDSvc`, `QuarkFileMD`, `QuarkContainerMD`, metadata setters/getters, `serialize`, `deserialize`, and checksum corruption.
Control flow: disabled `FileMd` test populates a file object with name, parent, times, size, uid/gid, layout, checksum, locations/unlinked locations, serializes/deserializes, compares environment output, then corrupts checksum and expects an exception. Disabled `ContainerMd` mirrors this for container fields and xattrs.
State/persistence: only in-memory `Buffer` serialization; no QDB backend.
Dependencies/integration: would depend on mocks, metadata concrete classes, and GMock expectations for listeners.
Risks: because tests are inactive, serialization regressions rely on integration reload tests rather than direct unit coverage; mock headers are also disabled.
Test signals: currently no active GTest cases in this file.
