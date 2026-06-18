# sources/cloud-native/buildkit/cache/contenthash/checksum.proto

Purpose: authoritative protobuf schema for serializing contenthash cache metadata.

Important APIs/types/functions: `CacheRecordType` enumerates file, directory recursive record, directory metadata header, and symlink. `CacheRecord` stores digest/type/linkname. `CacheRecordWithPath` pairs a normalized path key with a record. `CacheRecords` is a repeated list for the whole radix tree.

Control flow: schema-only. Runtime behavior is generated into standard protobuf and vtproto Go files.

State and persistence behavior: this schema is persisted into cache ref metadata. Path records map directly to the radix-tree layout documented in `checksum.go`, including the separate directory header/content convention.

Dependencies and integration points: Go package is `github.com/moby/buildkit/cache/contenthash`. Used exclusively by the contenthash cache manager.

Risks: changing enum values or field numbers is a persistent metadata migration. New fields should preserve backward compatibility with existing cache metadata.

Test signals: `TestPersistence` validates reload across cache-manager recreation; benchmarks validate generated vtproto serialization paths.
