# sources/cloud-native/nydus/service/src/uffd_proto.rs

Purpose: defines the JSON protocol used by the block-uffd feature for userfaultfd-style page-fault coordination between a client and server.

Important APIs/types: `UFFD_PROTOCOL_VERSION`, repr-serialized `MessageType` (`Handshake`, `PageFault`, `Stat`, `StatResp`), `FaultPolicy` (`Zerocopy`, `Copy`), `VmaRegion`, `HandshakeRequest`, `PageFaultResponse`, `BlobRange`, `StatRequest`, and `StatResponse`.

Control flow: constructors/defaults provide protocol defaults: handshake message type, zerocopy policy, read-only `prot`, `MAP_PRIVATE | MAP_FIXED` flags, `StatRequest::new`, and `StatResponse::new`. Actual transport and fault handling are implemented elsewhere; this file is schema-only.

State and persistence: all structures are serde serializable/deserializable. `VmaRegion` carries mapping coordinates, page size, optional `page_size_kib`, and mmap protection/flags; `PageFaultResponse` carries blob ranges to satisfy faults; `StatResponse` returns size/block/flags/version metadata.

Dependencies and integration: uses `serde`, `serde_repr`, and libc constants. The module is exported only on Linux with the `block-uffd` feature, coupling it to the block UFFD service path.

Risks: numeric enum encoding is wire-visible and must remain compatible; defaults affect clients that omit fields; mmap flags include `MAP_FIXED`, so consumers must validate address ranges carefully. There is no validation of region alignment, overlap, or protocol version in this schema file.

Test signals: tests cover enum defaults and numeric JSON encoding/decoding, `VmaRegion` constructor/default fields, handshake default type, blob/page-fault serialization, stat response construction, and fault-policy serialization.
