<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporterprovider/provider.go -->
# sources/cloud-native/buildkit/session/exporter/exporterprovider/provider.go

Purpose: small provider implementation for the session Exporter gRPC service backed by a callback.

Important APIs, types, and functions: `Callback` accepts context, metadata, and refs and returns exporter requests. `New(cb)` returns `*Exporter`. `Exporter.Register` registers the generated service. `FindExporters` calls the callback and wraps the result in `FindExportersResponse`, returning gRPC `Unavailable` when no callback is registered.

Control flow and state: state is only the callback. Each RPC delegates directly to it.

Dependencies and integration: depends on generated exporter gRPC code and standard gRPC status codes. Lets higher-level callers plug custom exporter discovery into a session.

Risks and test signals: nil callback is a runtime error. Callback errors are propagated directly. Tests should cover nil callback, metadata/ref propagation, and response wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporterprovider/provider.go -->
