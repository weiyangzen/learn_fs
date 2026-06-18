# sources/cloud-native/containerd/api/services/content/v1/content.proto

Protocol definition for containerd's content-addressable storage service. It describes metadata lookup/update, listing, deletion, ranged reads, ingest status, streaming writes, and abort behavior.

The `Content` service exposes unary `Info`, `Update`, `Delete`, `Status`, `ListStatuses`, `Abort`; server-streaming `List` and `Read`; and bidirectional-streaming `Write`. Data types include `Info` for committed blob metadata, `Status` for active ingests, `WriteAction` for stream behavior, and request/response wrappers. `WriteContentRequest` is the main state-transition message for ingests: it can stat, write at offset, or commit while validating total size and digest.

Control flow is defined by RPC semantics. `List` streams chunks of `Info`. `Read` streams one or more byte chunks from digest/offset/size. `Write` starts or resumes a ref, permits only one active stream per ref, expects non-overlapping offsets, can stat while holding the lock, and terminates on commit. `Abort` cancels a ref and frees resources.

Persistence is implemented elsewhere, but the proto defines durable content metadata and active ingest status. Dependencies are `Empty`, `FieldMask`, and `Timestamp`. Integration points include content store backends, image pull/unpack flows, diff uploads, garbage collection, label indexing, and generated transports.

Risks include ambiguous handling of zero-valued `WriteAction`, offset overlap/concurrency races, digest/size validation holes, large streaming datasets, regex/filter cost in status listing, and incorrect updates to immutable fields. Test signals should cover streaming read/write, commit validation, duplicate digest failures, abort cleanup, update masks, label limits, list filtering, and cancellation/backpressure behavior.
