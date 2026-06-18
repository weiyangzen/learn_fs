# sources/cloud-native/stargz-snapshotter/analyzer/recorder/recorder.go

Purpose: Maps accessed image paths back to the layer index that currently provides each file, then writes recorder entries for use as prioritized files during eStargz or zstd:chunked conversion.

Important APIs: `NewImageRecorder`, `Record`, `RecordGlob`, `Commit`, and `Close`. Internally, `imageRecorderFromManifest` builds a per-layer path index by reading and optionally decompressing each layer tar. `cleanEntryName` normalizes root-relative paths.

Control flow: Construction resolves the image manifest for a platform, reads manifest JSON, iterates layers, opens each layer blob, decompresses when needed, and scans tar headers into `filesMap`. `Record` normalizes a name, skips duplicates, searches layers from top to bottom, rejects paths masked by whiteout files or opaque directory whiteouts, then emits a `recorder.Entry` with manifest digest and layer index. `RecordGlob` lazily merges all paths and applies an injected matcher.

State and persistence: Holds path indexes, a content writer for the record stream, a duplicate set, and an all-path cache. `Commit` commits the content writer and returns its digest.

Dependencies and integration: Uses containerd content/images APIs, manifest selection helpers, tar/compression utilities, and the shared `recorder` package. Used by `ctr-remote optimize --prefetch-list`.

Risks: Layer scanning is potentially expensive and comments note duplicate decompression during optimization. `RecordGlob` ignores individual `Record` failures, which is intentional for deleted or missing entries but can hide unexpected problems.

Test signals: `recorder_test.go` verifies layer selection, overlay precedence, path normalization, compressed and uncompressed layers, and whiteout rejection.
