# Research: sources/cloud-native/buildkit/cmd/buildctl/debug/workers.go

Purpose: implements `buildctl debug workers`, the CLI display path for daemon worker inventory. It exposes filtering, templates, and verbose detail for platforms, labels, GC policies, versions, and CDI devices.

Important APIs and flow: `listWorkers` resolves the client, calls `Client.ListWorkers` with filter strings, and chooses template output, verbose output, or compact table output. `printWorkersVerbose` prints stable sorted label and annotation keys, BuildKit/Dockerfile versions, CDI device auto/on-demand mode, and every GC policy rule with human-readable units. `joinPlatforms` normalizes platform specs.

State and dependencies: reads daemon worker state only. It depends on the client worker adapter, common template parsing, tabwriter, platform formatting, sorted map iteration, unit formatting, and command context metadata.

Risks and test signals: verbose output is sensitive to nil/empty fields and map order, which sorted keys mitigate. Template mode ignores `--verbose`. Direct tests are absent, but the daemonless example uses this command as a readiness probe.
