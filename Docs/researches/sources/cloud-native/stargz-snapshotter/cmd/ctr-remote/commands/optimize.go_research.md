# sources/cloud-native/stargz-snapshotter/cmd/ctr-remote/commands/optimize.go

Purpose: Defines `ctr-remote images optimize`, which analyzes a workload or prefetch list, records accessed files, and converts the image with per-layer prioritized files for lazy pulling.

Important APIs: `OptimizeCommand`, `writeContentFile`, `readPrefetchList`, `buildLayerOptsFromRecord`, `analyzePrefetchList`, `analyze`, `isReusableESGZLayer`, `excludeWrapper`, and `logWrapper`.

Control flow: The command validates refs and flags, selects platforms, opens a containerd client/lease, runs `analyze`, optionally writes the record content to a file, builds an eStargz or zstd:chunked converter with per-layer options, wraps conversion for reuse/logging, handles interrupts, runs `converter.Convert`, performs external TOC finalization if configured, and prints digests. `analyze` can skip optimization, consume `--prefetch-list`, or run a sampled container through `analyzer.Analyze`. Prefetch-list paths can be exact or glob patterns matched by doublestar.

State and persistence: Reads/writes containerd content and images. Records are content blobs and optionally filesystem files. Conversion may create an extra TOC image.

Dependencies and integration: Central integration point for analyzer, recorder, native converters, containerd converter APIs, platform helpers, gzip helpers, and zstd.

Risks: Reuse is digest-keyed with a TODO noting layer index would be better. `RecordGlob` misses are logged but not fatal. External TOC and reuse are disallowed together. Analysis only runs for default platform unless all-platforms or matching platform flags allow it.

Test signals: No direct tests in this subset; multiple branches need CLI/integration coverage.
