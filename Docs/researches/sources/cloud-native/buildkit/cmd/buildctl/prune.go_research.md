# Research: sources/cloud-native/buildkit/cmd/buildctl/prune.go

Purpose: implements `buildctl prune`, the cache cleanup command that streams records removed by daemon workers and summarizes reclaimed space.

Important APIs and flow: `pruneCommand` defines keep-duration, storage thresholds, filters, `--all`, verbose, and format flags. `prune` resolves the client, builds `client.PruneOption` values with filter and keep settings, appends `client.PruneAll` when requested, starts an output goroutine for template or table/verbose mode, invokes `c.Prune` with a channel, closes the channel, waits for printing, returns prune errors, and prints total reclaimed bytes when applicable.

State and dependencies: mutates daemon cache state through worker prune operations; local state is only a streaming channel and summary counter. Depends on client prune options, common templates, tabwriter, units, and disk usage row printers shared with `du`.

Risks and test signals: template output panics inside the goroutine on write/template errors, which would crash rather than return a normal error. `prune_test.go` smoke-tests successful integration execution but not filters, keep thresholds, all mode, or output formatting.
