# sources/distributed-fs/eos/namespace/ns_quarkdb/persistency/Serialization.cc

Purpose: Implements deserialization helpers for EOS metadata protobuf buffers and integer values with checksum/status handling.
Important APIs/types/functions: overloaded `deserializeNoThrow` for `FileMdProto`, `ContainerMdProto`, and `int64_t`; throwing wrappers `deserializeFile` and `deserializeContainer`.
Control flow: protobuf buffer decoding reads a CRC32C and object-size prefix, computes CRC32C over the remaining aligned payload, compares checksums, then parses protobuf through `google::protobuf::io::ArrayInputStream`. Integer decoding copies bytes into a null-terminated string and validates `strtoll` consumed the full input.
State/persistence: no retained state; it interprets the persisted binary layout produced by metadata serialization.
Dependencies/integration: depends on `Buffer`, `DataHelper` CRC32C, generated protobuf classes, `MDStatus`, and `MDException`.
Risks: the implementation assumes buffers contain at least two 32-bit fields; malformed/truncated buffers may read before returning `MDStatus`; `align_size` includes any padding while parser uses `obj_size`, so serialization format compatibility is strict.
Test signals: currently active tests do not directly cover this file; disabled `MetadataTests.cc` code shows intended checksum-corruption checks for file/container metadata.
