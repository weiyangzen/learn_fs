## sources/cloud-native/moby/daemon/builder/dockerfile/dispatchers.go

**Purpose:** Implements Dockerfile instruction handlers for the classic builder.

**Important APIs:** Dispatchers include `dispatchEnv`, `dispatchMaintainer`, `dispatchLabel`, `dispatchAdd`, `dispatchCopy`, `initializeStage`, `dispatchTriggeredOnBuild`, `getExpandedString`, `getImageOrStage`, `getFromImage`, `dispatchOnbuild`, `dispatchWorkdir`, `dispatchRun`, `prependEnvOnCmd`, `dispatchCmd`, `dispatchHealthcheck`, `dispatchEntrypoint`, `dispatchExpose`, port parsing helpers, `dispatchUser`, `dispatchVolume`, `dispatchStopSignal`, `dispatchArg`, and `dispatchShell`.

**Control flow:** `FROM` resolves platform and image/stage references, resets cache, starts dispatch state, and runs ONBUILD triggers. Metadata commands mutate run config and commit NOP layers. `RUN` builds cache config, creates/runs a container on miss, converts nonzero exit to JSON stream error, and commits. ADD/COPY delegate to copier and performCopy. EXPOSE parses Docker port syntax.

**State and persistence:** Mutates `dispatchState.runConfig`, build args, image ID, and stage results. Commits images/layers through builder internals. Records cache history through NOP command strings.

**Dependencies and integration:** Uses BuildKit instruction AST types, shell expansion, daemon image/cache/container backends, network port types, signal parsing, and platform parsing.

**Risks:** This is compatibility-critical. Cache key strings, Windows `ArgsEscaped`, ONBUILD recursion, build-arg transparency, and port parsing all affect user-visible behavior. Unsupported BuildKit-only flags must fail clearly.

**Test signals:** `dispatchers_test.go`, platform-specific dispatcher tests, and evaluator tests cover many handlers, port parsing, build args, unsupported options, and workdir normalization.
