# sources/distributed-fs/juicefs/pkg/object/response_attrs.go

Purpose: defines a small opt-in attribute propagation mechanism for object operations, allowing backends to return request IDs, storage class, and request size without changing method signatures.

Important APIs and types: `ResponseAttrs` holds pointer fields for requested attributes. `AttrGetter` is a function that installs pointers into a `ResponseAttrs`. Constructors are `WithRequestID`, `WithStorageClass`, and `WithRequestSize`; `ApplyGetters` applies all getters and returns the mutable carrier. `DefaultStorageClass` is `"STANDARD"`.

Control flow and state: backends call `ApplyGetters(getters...)`, then invoke setters on the returned value. Setters only mutate non-nil pointers, making attributes optional and allocation-free for uninterested callers. `SetStorageClass` ignores empty strings to avoid overwriting a caller's existing/default storage class. `GetRequestSize` returns `-1` when request size was not requested.

Persistence and integration: no persistent state. It is integrated into S3, OSS, TOS, QingStor, UFile-style paths, and delete/get/put operations where providers expose request metadata.

Risks and test signals: pointer ownership remains with callers, so concurrent reuse of the same target variable could race. Empty storage classes are intentionally ignored. Tests in `response_attrs_test.go` cover request ID and non-empty storage class propagation.
