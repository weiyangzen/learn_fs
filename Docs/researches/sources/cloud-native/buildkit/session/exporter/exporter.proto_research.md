<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter.proto -->
# sources/cloud-native/buildkit/session/exporter/exporter.proto

Purpose: protobuf contract for discovering exporter requests through a BuildKit session.

Important APIs, types, and functions: package `moby.exporter.v1`, Go package `github.com/moby/buildkit/session/exporter`. Service `Exporter` exposes unary `FindExporters`. Request carries `map<string, bytes> metadata` and repeated refs. Response carries repeated `ExporterRequest`, each with string `Type` and string map `Attrs`.

Control flow and state: schema only. Runtime state is in request/response messages and provider callbacks.

Dependencies and integration: drives generated Go, gRPC, and vtproto code, and is implemented by `exporterprovider.Provider`.

Risks and test signals: map value bytes allow opaque metadata but require callers to agree on encoding. Field-name capitalization `Type` and `Attrs` is preserved in generated Go. Test by callback integration and wire compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter.proto -->
