# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/epoch.go

Purpose: resolves Dockerfile `SOURCE_DATE_EPOCH` values into timestamps, including numeric values, main/named contexts, or a restricted source-only stage that points at an HTTP/Git remote.

Important APIs: `resolveSourceDateEpochValue`, `formatSourceDateEpochValue`, `resolveSourceDateEpochState`, `sourceDateEpochStageSource`, `applySourceDateEpochStageArgs`, `sourceDateEpochAddSource`, `resolveSourceDateEpochFromState`, `sourceOpFromState`, `sourceDateEpochFromMetadata`, and `archiveMaxTimeFromRef`.

Control flow: numeric values become UTC Unix seconds. `context` loads main context; named contexts are checked through dockerui; stage names must resolve to `FROM scratch` stages containing only ARG and exactly one remote ADD. Remote ADD sources become HTTP or Git LLB sources with checksum/subdir/submodule flags. Metadata resolution prefers Git commit object committer time or HTTP Last-Modified. For HTTP archives without metadata, it solves and scans archive members for max mtime.

State and persistence: no durable state; resolved epoch is stored in `dispatchState` and build args, then exported as metadata/history timestamps.

Dependencies and integration: bridges Dockerfile conversion, dockerui gateway client, sourceresolver metadata, git object parsing, archive decompression, and source op protobuf extraction.

Risks and test signals: risks include ambiguous states with multiple source ops, archive decompression fallback, symbolic value behavior without client, stage restriction enforcement, and Git checksum parity. `convert_test.go` covers numeric/context/stage/source-op paths.
