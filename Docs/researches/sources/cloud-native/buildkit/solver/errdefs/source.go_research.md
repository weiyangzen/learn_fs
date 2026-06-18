<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/source.go -->
## sources/cloud-native/buildkit/solver/errdefs/source.go

Purpose: attaches source-location details to errors and can print highlighted source excerpts.

Important APIs and types: `WithSource`, `SourceError`, `Sources(err)`, `(*Source).WrapError`, and `(*Source).Print`. Helpers `containsLine` and `getStartEndLine` inspect protobuf ranges.

Control flow: `Sources` recursively unwraps `SourceError` chains and appends cloned details. `Print` splits embedded source data into lines, finds the min/max range, pads surrounding context, and writes a filename header plus marked `>>>` lines.

State and dependencies: no persistence; `Print` only writes to an `io.Writer`. Dependencies include `solver/pb` source/range messages, `grpcerrors`, and `pkg/errors`.

Integration points: used by frontend/source parsing paths to surface precise Dockerfile or LLB source locations in error details and client diagnostics.

Risks and test signals: `Print` ignores nil/malformed ranges and out-of-bounds starts, which is safe but may hide context. Multi-range printing highlights all contained lines but computes a single padded span. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/errdefs/source.go -->
