## sources/cloud-native/buildkit/session/sshforward/ssh_vtproto.pb.go

Purpose: generated vtprotobuf helpers for faster clone, equality, marshal, size, and unmarshal operations on SSH protobuf messages.

Important APIs/types/functions: provides `CloneVT`, `CloneMessageVT`, `EqualVT`, `EqualMessageVT`, `MarshalVT`, `MarshalToVT`, `MarshalToSizedBufferVT`, `SizeVT`, and `UnmarshalVT` for `BytesMessage`, `CheckAgentRequest`, and `CheckAgentResponse`. The unmarshal paths parse protobuf wire types, skip unknown fields, and return explicit errors for illegal tags or malformed varints.

Control flow: generated marshal methods write fields in reverse into sized buffers; unmarshal loops over field numbers and wire types, appending byte fields and strings where present. Empty response methods are mostly no-ops plus unknown-field skipping.

State and persistence: only per-message byte slices and strings are manipulated. Unknown fields are skipped rather than retained by these helpers.

Dependencies and integration points: used by protobuf/gRPC runtime or optimized call sites when vtproto methods are detected. It complements, not replaces, `ssh.pb.go`.

Risks and test signals: generated code must match `ssh.proto` field numbers exactly. The biggest operational risk is stale generation after schema edits. Functional stream coverage in `raw_provider_test.go` indirectly verifies message transmission, while vtproto-specific wire edge cases are not tested in this subset.
