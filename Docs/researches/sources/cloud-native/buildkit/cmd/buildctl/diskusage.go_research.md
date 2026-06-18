# Research: sources/cloud-native/buildkit/cmd/buildctl/diskusage.go

Purpose: implements `buildctl du`, a cache disk usage inspection command. It retrieves usage records from the daemon and renders table, verbose, or template output.

Important APIs and flow: `diskUsage` resolves the client, calls `c.DiskUsage` with filter options, chooses template mode if requested, otherwise prints verbose records or a compact table, and prints aggregate summary when no filter is applied. Helpers print key/value records, table headers/rows, and total/reclaimable/shared/private byte summaries.

State and dependencies: reads daemon worker disk usage state without mutating it. It depends on client disk usage APIs, common template parsing, tabwriter, BuildKit logging for ignored verbose mode, and human-readable units.

Risks and test signals: compact table omits `Last accessed` content despite the header, and formatting appends markers for mutable/shared records. `diskusage_test.go` only smoke-tests command success in integration, so output details need manual/golden coverage for regressions.
