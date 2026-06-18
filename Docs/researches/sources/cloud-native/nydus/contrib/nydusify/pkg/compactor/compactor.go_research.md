# sources/cloud-native/nydus/contrib/nydusify/pkg/compactor/compactor.go

Purpose: wraps `nydus-image compact` to compact Nydus blobs/bootstrap using configurable thresholds.

Important APIs and flow: `CompactConfig` stores min used ratio, compact blob size, max compact size, layers to compact, and blobs directory. `Dumps` writes JSON config; `loadCompactConfig` reads it. `NewCompactor` loads a config or uses defaults, sets `BlobsDir` to the workdir, and creates a build `Builder`. `Compact` removes stale `<bootstrap>.compact` and `compact-result.json`, calls `builder.Compact` with chunk dictionary, backend, output paths, and config thresholds, then returns the target bootstrap path.

State and persistence: reads/writes config files, removes old output files, writes compact output through the external builder command.

Dependencies and integration: integrates with `pkg/build.Builder` and Nydus compact CLI options. Intended to be used in conversion/optimization flows after bootstrap creation.

Risks and test signals: all numeric config values are strings and are not validated before command execution. `BlobsDir` from config is always overwritten by workdir. Output JSON is removed and regenerated but not parsed here.
