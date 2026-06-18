<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter_grpc.pb.go -->
# sources/cloud-native/buildkit/session/exporter/exporter_grpc.pb.go

Purpose: generated gRPC bindings for the Exporter session service.

Important APIs, types, and functions: defines `ExporterClient`, `FindExporters` client call, `ExporterServer`, `UnimplementedExporterServer`, `UnsafeExporterServer`, `RegisterExporterServer`, service descriptor, and unary handler.

Control flow and state: client invokes `/moby.exporter.v1.Exporter/FindExporters`; server handler decodes request, applies optional interceptor, and dispatches to implementation.

Dependencies and integration: used by session exporter discovery providers and callers over gRPC.

Risks and test signals: service and method names are compatibility-sensitive. Generated code should be regenerated from proto. Test through provider registration and client calls.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter_grpc.pb.go -->
