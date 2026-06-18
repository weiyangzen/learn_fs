<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter_vtproto.pb.go -->
# sources/cloud-native/buildkit/session/exporter/exporter_vtproto.pb.go

Purpose: vtprotobuf optimized clone, equality, marshal, size, and unmarshal helpers for exporter protobuf messages.

Important APIs, types, and functions: implements `CloneVT`, `EqualVT`, `MarshalVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT` for `FindExportersRequest`, `FindExportersResponse`, and `ExporterRequest`.

Control flow and state: generated code handles repeated exporter slices, string maps, byte maps, unknown fields, and protobuf wire parsing.

Dependencies and integration: used by protobuf fast paths in BuildKit session exporter code.

Risks and test signals: map ordering and deep-copy behavior matter for deterministic equality and clone independence. Regenerate after schema changes and run protobuf round-trip tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/exporter/exporter_vtproto.pb.go -->
