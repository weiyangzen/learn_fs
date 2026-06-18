# sources/cloud-native/buildkit/client/llb/state_test.go

Purpose: tests state metadata, image/blob source validation, source-map marshaling, and platform propagation across state graph operations.

Important APIs/types/functions: `TestStateMeta`, `TestFormattingPatterns`, `TestImageBlobInvalid`, `TestImageBlobSource`, `TestOCILayoutBlobSource`, `TestStateSourceMapMarshal`, `TestPlatformFromImage`, `TestPlatformFromImageWithMerge`, and helper `getEnvHelper`.

Control flow: tests build states, query metadata, marshal definitions, decode protobuf ops, inspect source identifiers/attrs/source maps/platforms, and compare expected graph shapes. Source-map test checks deduplication and range ordering across repeated maps and merge. Platform tests verify file ops are platform-neutral while image/exec inherit correct platform through copy and merge graphs.

State and persistence: in-memory state graphs and protobuf definitions only.

Dependencies/integration points: image/blob constructors, OCI blob store attrs, source maps, merge/file/exec/image sources, platform constraints, parse helpers, and metadata getters.

Risks/test signals: good coverage for API-visible metadata and platform behavior. It does not execute graphs or test every source option.
