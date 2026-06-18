# sources/cloud-native/nydus-snapshotter/pkg/converter/tool/builder.go

Purpose: wraps the external `nydus-image` CLI for pack, merge, and unpack operations with structured option types and timeout support.

Important APIs and functions: option structs `PackOption`, `MergeOption`, `UnpackOption`; `buildPackArgs`; exported `Pack`, `Merge`, and `Unpack`; helper `packRef`; `isSignalKilled`; internal `outputJSON`.

Control flow: `Pack` delegates to `packRef` for OCI reference mode or builds `nydus-image create` args. It defaults fs version to 6, sets prefetch/whiteout/blob/fs flags, chooses tar-rafs or directory flags based on detected features, adds chunk dict, compressor, alignment, chunk/batch size, encryption, and source path, then runs the command with optional timeout and prefetch patterns on stdin. `Merge` builds `nydus-image merge` args with source bootstraps, blob digests/TOC digests/sizes, chunk dict/parent bootstrap, output JSON, and parses resulting blob IDs into SHA256 digests. `Unpack` builds `nydus-image unpack`, optionally translates a nested backend config file into `--backend-type` and `--backend-config`, or passes a blob path.

State and persistence: external commands read/write paths provided by converter code. `Merge` reads output JSON from disk. Logging goes through logrus logger writers. No in-process persistence.

Dependencies and integration points: used by `convert_unix.go` and `reconvert_unix.go`; depends on `nydus-image` CLI compatibility and feature detection from `feature.go`.

Risks: command argument construction is tightly coupled to nydus-image versions. Timeout detection relies on error text containing `signal: killed`. `Unpack` type-asserts backend config JSON shapes and can panic if `backend` is missing or not a map before the `ok` check on nested access. `Merge` assumes output blob IDs are hex SHA256 strings.

Test signals: no direct builder command tests in listed files; feature tests cover feature-detection inputs that influence `buildPackArgs`.
