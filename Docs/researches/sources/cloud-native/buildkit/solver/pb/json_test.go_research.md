# sources/cloud-native/buildkit/solver/pb/json_test.go

Purpose: this test file validates the custom JSON round-trip behavior implemented in `json.go` for `Op`, `FileAction`, and `UserOpt` protobuf messages. It ensures the JSON shape is stable and that marshaled JSON can unmarshal back into equivalent Go protobuf structs.

Important APIs and tests: `TestJSON_Op` covers exec, source, file, build, merge, and diff operations. It checks both exact structural JSON equivalence and unmarshal equality. `TestJSON_FileAction` covers copy, mkfile, mkdir, and rm actions, including byte data encoding for `mkfile` as base64 JSON. `TestJSON_UserOpt` covers `UserOpt_ByName` and `UserOpt_ByID`. The tests use `encoding/json` and `testify/require`.

Control flow: each test defines a table of named cases with a protobuf value and an expected JSON string. For each case, it marshals the protobuf value, unmarshals both actual and expected JSON into `any` to avoid formatting/key-order sensitivity, and compares the resulting structures. It then unmarshals the actual bytes into a fresh protobuf object and requires deep equality with the original.

State and persistence: there is no persistent state. The expected JSON strings are the contract under test. They capture omitempty behavior, nested `Op` / `Action` / `User` wrapper object names, default numeric fields that remain visible in custom file-action JSON, and protobuf byte-to-base64 encoding for raw file contents.

Dependencies and integration points: these tests integrate directly with `json.go` and the generated types in `ops.pb.go`. They are important for frontend/debugging compatibility because the custom JSON layout is manually maintained in parallel with `ops.proto`.

Risks and test signals: the tests provide strong signal for currently-covered oneof variants but expose omissions by absence. `PassthroughOp` is handled in `json.go` but not covered here, and `FileActionSymlink` exists in the schema/generated code but is not represented or tested in `json.go`. There is also no test for invalid JSON, JSON containing multiple oneof branches, or empty `UserOpt` behavior.
