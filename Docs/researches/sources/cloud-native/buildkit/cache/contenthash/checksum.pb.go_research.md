# sources/cloud-native/buildkit/cache/contenthash/checksum.pb.go

Purpose: generated Go protobuf bindings for the persisted contenthash cache record schema.

Important APIs/types/functions: enum `CacheRecordType` with `FILE`, `DIR`, `DIR_HEADER`, and `SYMLINK`; messages `CacheRecord`, `CacheRecordWithPath`, and `CacheRecords`; getters and reflection descriptors. The generated constants are re-exported by `checksum.go` as package-level aliases.

Control flow: no business logic. Init builds enum/message descriptors and exporter metadata for protobuf reflection. Getter methods return defaults for nil receivers.

State and persistence behavior: this is the wire format used by `cacheContext.save/load` under metadata key `buildkit.contenthash.v0`. Each radix entry persists as path plus record containing digest, type, and symlink target.

Dependencies and integration points: protobuf runtime/reflection packages. The vtproto file supplies high-performance marshal/unmarshal used directly by `checksum.go`.

Risks: schema/tag changes can make old metadata unreadable or semantically wrong. Generated code should not be edited manually.

Test signals: `TestPersistence` exercises saved `CacheRecords`; `checksum_bench_test.go` benchmarks marshal/unmarshal for representative records.
