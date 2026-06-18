# sources/cloud-native/stargz-snapshotter/cmd/containerd-stargz-grpc/db/db.go

Purpose: Defines the bbolt schema and low-level encode/decode helpers for the persistent metadata reader used by the snapshotter and store.

Important APIs/types: Bucket key variables, `childEntry`, `chunkEntry`, `metadataEntry`, bucket accessors (`getNodes`, `getMetadata`, `getStream`), attribute helpers (`writeAttr`, `readAttr`), child/chunk helpers (`readChild`, `readChunks`, `readInnerChunks`, `writeMetadataEntry`), and binary encoders.

Control flow: Metadata is stored under `filesystems/<fsID>` with `nodes`, `metadata`, and `stream` buckets. Node buckets hold attributes. Metadata buckets hold first child/chunk inline and overflow entries in sub-buckets to avoid bucket creation for common single-entry cases. Stream buckets map compressed stream offsets to node ids when multiple chunks share a compressed stream.

State and persistence: Persists filesystem metadata in bbolt. Integers use varint/uvarint except ids and chunk entries, which use big-endian fixed fields for ordered keys and compact chunk payloads.

Dependencies and integration: Used heavily by `reader.go`; depends on `metadata.Attr` and bbolt.

Risks: `decodeID` assumes at least four bytes; corrupted DB data can panic or decode incorrectly. `readAttr` stores byte slices directly from bbolt values; callers should treat them as transaction-scoped. Map iteration chooses arbitrary first child/xattr, which is acceptable for storage but non-deterministic internally.

Test signals: Covered indirectly by `reader_test.go` through metadata reader, filesystem reader, and layer suites.
