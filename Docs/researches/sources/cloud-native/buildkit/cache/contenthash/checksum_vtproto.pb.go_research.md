# sources/cloud-native/buildkit/cache/contenthash/checksum_vtproto.pb.go

Purpose: vtproto-generated fast clone/equality/serialization implementation for the contenthash persistence schema.

Important APIs/types/functions: `CloneVT`, `EqualVT`, `MarshalVT`, `MarshalToVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT` for `CacheRecord`, `CacheRecordWithPath`, and `CacheRecords`.

Control flow: marshal methods write protobuf fields manually into sized buffers; unmarshal methods parse wire fields and append repeated path records. Clone methods deep-copy nested records and repeated slices. Equality compares nested messages and ordered path slices.

State and persistence behavior: used by `cacheContext.load/save` to serialize the complete radix tree payload. It shares the exact wire schema from `checksum.proto` and introduces no additional state.

Dependencies and integration points: uses protobuf `proto.Message` interfaces for compatibility. Benchmarks in this subset call `MarshalVT` and `UnmarshalVT` directly.

Risks: ordered repeated `Paths` means semantic equality depends on deterministic tree walk order in `save`. Generated parsing must be regenerated on schema changes. Unknown fields are skipped in these fast paths.

Test signals: `TestPersistence` and `checksum_bench_test.go` provide direct signals that vtproto bytes round-trip enough for persisted cache records.
