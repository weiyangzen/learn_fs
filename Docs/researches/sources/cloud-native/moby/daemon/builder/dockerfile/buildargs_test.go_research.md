## sources/cloud-native/moby/daemon/builder/dockerfile/buildargs_test.go

**Purpose:** Unit tests for build-arg lookup, meta-arg handling, unused-arg warnings, and builtin proxy arg reference behavior.

**Important APIs:** Tests call `NewBuildArgs`, `AddArg`, `AddMetaArg`, `GetAllAllowed`, `GetAllMeta`, `WarnOnUnusedBuildArgs`, and `IsReferencedOrNotBuiltin`.

**Control flow:** Table-like assertions construct option/default values, then compare resulting maps or output text. The builtin test asserts an unreferenced proxy arg is treated transparently.

**State and persistence:** Uses in-memory `BuildArgs`; no filesystem or daemon state.

**Dependencies and integration:** Uses Go testing and buffers. It protects semantics used by `RUN`, `FROM`, and build cache formation.

**Risks:** Tests are narrow and do not cover `FilterAllowed`, clone merging, or nil-option edge cases exhaustively.

**Test signals:** Strong direct signal for the most visible `BuildArgs` behaviors: precedence, warnings, and builtin transparency.
