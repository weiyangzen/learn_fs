# sources/cloud-native/buildkit/exporter/local/export.go

Purpose: implements the `local` exporter, which streams build result files from BuildKit back to a client-side directory through the active session. The exporter handles single-result refs, multi-platform refs, optional platform directory splitting, local exporter modes, attestation files, and reproducible timestamps via `SOURCE_DATE_EPOCH`.

Important APIs and functions: `Opt` carries the `session.Manager`; `New` returns an `exporter.Exporter`; `Resolve` validates `CreateFSOpts`; `localExporterInstance` implements exporter metadata and `Export`; `NewProgressHandler` emits throttled progress updates and returns an explicit closer. `Export` resolves session caller access, parses platform metadata with `exptypes.ParsePlatforms`, builds filtered `fsutil.FS` values through `CreateFS`, and calls `filesync.CopyToCaller`.

Control flow: export options are loaded before runtime. During export, epoch is inherited from source metadata when not explicitly configured. Multi-platform inputs must include exporter platform mapping; without `platform-split`, duplicate output paths across platforms are rejected. Delete mode merges all output filesystems and transfers with `WithExporterMultiPlatformTransfer`; copy mode runs one transfer per platform using `errgroup`.

State and persistence: no durable server-side state is created, but mounted refs require cleanup; temporary progress state is in the progress writer. Shared `visitedPath` is protected by a mutex to detect collisions. Output persistence happens on the client through the filesync session.

Dependencies and integration: integrates cache refs, exporter source metadata, session/filesync, `CreateFS`, `staticfs.MergeFS`, epoch utilities, and BuildKit client exporter modes. Platform IDs are converted to safe directory names by replacing `/` with `_`.

Risks and test signals: main risks are missing platform mappings, platform path collisions when split is disabled, session lookup timeouts, cleanup leaks, and progress writer leaks. The progress closer comment signals a prior cleanup concern. Behavior is exercised indirectly by local/tar exporter integration tests and by epoch parsing tests.
