# sources/cloud-native/buildkit/solver/pb/json.go

Purpose: this file provides custom JSON marshaling and unmarshaling for protobuf messages that contain oneof fields: `Op`, `FileAction`, and `UserOpt`. The generated protobuf JSON shape is not used here; instead the package exposes a stable, readable JSON object layout for LLB debugging and round-tripping.

Important APIs and types: `jsonOp` wraps `Op` with `inputs`, an `Op` object containing optional `exec`, `source`, `file`, `build`, `merge`, `diff`, and `passthrough` fields, plus `platform` and `constraints`. `(*Op).MarshalJSON` and `(*Op).UnmarshalJSON` translate between protobuf oneof wrappers and that JSON structure. `jsonFileAction` exposes `input`, `secondaryInput`, `output`, and an `Action` object with optional `copy`, `mkfile`, `mkdir`, and `rm` fields. `(*FileAction).MarshalJSON` and `(*FileAction).UnmarshalJSON` map the file-action oneof. `jsonUserOpt`, `(*UserOpt).MarshalJSON`, and `(*UserOpt).UnmarshalJSON` encode named user vs numeric ID options.

Control flow: each marshal method copies scalar fields into the JSON wrapper, type-switches on the active oneof wrapper, sets the corresponding pointer field, and calls `json.Marshal`. Each unmarshal method decodes into the wrapper, copies scalar fields back, and selects the first non-nil oneof option in a fixed order. `UserOpt.UnmarshalJSON` defaults to `ByID` even when `byId` is absent, which means an empty user object decodes as ID zero.

State and persistence: no package state is stored. The persistent behavior is the JSON representation itself. Because `ops.proto` comments require changes to selected oneof-bearing structures to be reflected in `json.go`, this file is part of the compatibility surface whenever new op, file action, or user option variants are added.

Dependencies and integration points: direct dependency is `encoding/json`; structural dependencies are the generated protobuf types in `ops.pb.go`. It is integrated with `json_test.go`, with LLB debugging/export tooling, and with any code that expects these custom JSON keys rather than default protobuf JSON.

Risks and test signals: a current compatibility gap is that `ops.proto` and `ops.pb.go` include `FileActionSymlink`, but `jsonFileAction` does not include a symlink branch. Symlink file actions therefore cannot round-trip through this custom JSON path. Another risk is silent precedence when JSON contains multiple oneof branches. Tests cover the listed op variants, copy/mkfile/mkdir/rm file actions, and user by-name/by-ID cases, but not symlink or malformed multi-oneof input.
