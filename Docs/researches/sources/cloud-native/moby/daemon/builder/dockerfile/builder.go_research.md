## sources/cloud-native/moby/daemon/builder/dockerfile/builder.go

**Purpose:** Implements the classic Dockerfile builder orchestration: context detection, builder initialization, Dockerfile parsing, stage execution, cache use, progress output, and commit-change support.

**Important APIs/types:** `BuildManager` owns daemon backend, path cache, and ID mapping. `NewBuildManager`, `Build`, `builderOptions`, `Builder`, `newBuilder`, `buildLabelOptions`, `build`, `emitImageID`, `processMetaArg`, `printCommand`, `dispatchDockerfileWithCancellation`, `BuildFromConfig`, and conversion helpers are key.

**Control flow:** `BuildManager.Build` defaults Dockerfile name, detects remote/archive context, creates a cancellable context and `Builder`, then runs `build`. `build` parses stages/meta args, applies target truncation and CLI labels, prints warnings, dispatches stages, and returns image ID. Dispatch loops process meta args first, then each `FROM` stage and instruction with cancellation checks.

**State and persistence:** Uses a shared `syncmap` path cache for copy hashes, per-build `imageSources`, `containerManager`, `imageProber`, and build args. Persistent outputs are committed images/layers through backend methods.

**Dependencies and integration:** Depends on BuildKit Dockerfile parser/instructions, remotecontext, daemon builder interfaces, platform parsing, metrics, and progress writers.

**Risks:** Classic builder compatibility depends on exact output formatting, stage order, label sorting, and cache-key command strings. Context cleanup is deferred and must run after all source users finish.

**Test signals:** Broader behavior is covered by dispatcher/internals tests plus daemon integration tests. Direct risks include target selection, meta arg expansion, empty Dockerfile errors, and commit-change command whitelist.
