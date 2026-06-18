<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets_vtproto.pb.go -->
# sources/cloud-native/buildkit/session/secrets/secrets_vtproto.pb.go

Purpose: vtprotobuf optimized helpers for secret protobuf messages.

Important APIs, types, and functions: implements clone, equality, marshal, size, and unmarshal methods for `GetSecretRequest` and `GetSecretResponse`, including annotations map handling and data byte copying.

Control flow and state: generated code deep-copies maps/slices, preserves unknown fields, and parses protobuf wire format.

Dependencies and integration: used by fast protobuf paths for secrets session messages.

Risks and test signals: map clone/equality behavior is important for annotations. Regenerate after schema changes and test round trips plus clone independence.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/session/secrets/secrets_vtproto.pb.go -->
