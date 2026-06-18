# sources/cloud-native/buildkit/client/llb/sourcemap.go

Purpose: attaches source-code location metadata to LLB vertices so solver errors can point back to frontend source files and ranges.

Important APIs/types/functions: `SourceMap` stores optional state/definition, filename, language, and source data. `NewSourceMap` constructs it. `Location` returns a constraints option adding a `SourceLocation`. `equalSourceMap` deduplicates source maps. `sourceMapCollector` accumulates maps and digest-to-location mappings and marshals to `pb.Source`.

Control flow: frontend code creates a source map and passes `Location` as a constraints option. During state marshal, vertices return source locations; the collector deduplicates source maps by pointer or structural equality, later marshals each source map, recursively marshaling attached state if needed, and emits `pb.SourceInfo` plus per-digest locations.

State and persistence: source map definitions are cached in the `SourceMap.Definition` field after first marshal. Collector state is per-definition marshal.

Dependencies/integration points: `state.go` marshal flow, protobuf source/range structures, frontend error reporting, and source-map tests in `state_test.go`.

Risks/test signals: `equalSourceMap` accesses the last definition entry when both definitions are non-nil and one length is zero because its length check uses `&&`; this could panic for empty definitions. Recursive state marshaling can be expensive. Tests cover deduplication and multiple ranges but not empty-definition equality edge cases.
