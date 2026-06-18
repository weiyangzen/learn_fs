<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter.pb.go -->
# sources/cloud-native/buildkit/session/exporter/exporter.pb.go

Purpose: generated protobuf message definitions for the session Exporter service.

Important APIs, types, and functions: defines `FindExportersRequest` with metadata map and refs, `FindExportersResponse` with repeated exporter requests, and `ExporterRequest` with type and attrs. Generated methods include standard protobuf reflection, getters, descriptor compression, and file initialization.

Control flow and state: generated descriptor state is initialized once. Message state is per-instance protobuf runtime data.

Dependencies and integration: generated from `exporter.proto`; used by exporterprovider and generated gRPC stubs.

Risks and test signals: field numbers are external wire contracts. Generated file should not be edited manually. Tests should operate through exporterprovider callback behavior and protobuf round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter.pb.go -->
