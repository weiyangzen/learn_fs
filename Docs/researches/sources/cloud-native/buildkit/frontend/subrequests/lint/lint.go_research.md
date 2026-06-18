<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/lint/lint.go -->
# sources/cloud-native/buildkit/frontend/subrequests/lint/lint.go

Purpose: defines the Dockerfile lint subrequest result model, JSON/text output generation, warning source mapping, and status-code metadata.

Important APIs, types, and functions: `RequestLint` and `SubrequestLintDefinition` expose `frontend.lint` version `1.0.0` with `result.json`, `result.txt`, and `result.statuscode`. `Warning` captures rule name, description, URL, detail, and protobuf location. `BuildError` records a build error and source location. `LintResults` contains warnings, source infos, and optional build error. `AddSource` deduplicates `llb.SourceMap` data into `pb.SourceInfo`. `AddWarning` converts parser ranges into `pb.Range` values. `ToResult` emits JSON, text, status code, and version. `PrintTo`, `PrintErrorTo`, `validateWarnings`, and `PrintLintViolations` render and validate warnings.

Control flow and state: lint collection is in-memory. Sources are appended only when filename, language, and raw data differ. Text output validates warning source indexes, sorts warnings by missing/known location, filename, line, then rule name, and renders BuildKit source snippets through `errdefs.Source.Print`.

Dependencies and integration: depends on Dockerfile parser ranges, LLB source maps, gateway result metadata, solver protobuf location/source types, and `errdefs.Source` formatting. It is a frontend subrequest result contract consumed by CLI and API clients.

Risks and test signals: `Warning.PrintTo` dereferences `Location` and `SourceIndex` without nil checks, so producers must always populate valid locations or validate before printing. `validateWarnings` checks out-of-range indexes but only checks nil sources when `SourceIndex > 0`, leaving index 0 nil as a possible panic path. Tests should cover sorting, source dedupe, status-code behavior, invalid source indexes, and build-error rendering.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/frontend/subrequests/lint/lint.go -->
