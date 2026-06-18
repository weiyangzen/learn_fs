# sources/distributed-fs/ipfs-kubo/test/cli/provide_stats_test.go

Purpose: validates `ipfs provide stat` output, flags, formats, provider-mode differences, integration with scheduled content, documented metrics, and disabled-provider behavior.

Important APIs and types: constants set polling timeout/tick. `sweepStats` mirrors the JSON fields used by tests, and `parseSweepStats` unmarshals `--enc=json` output. The suite configures `Provide.DHT.SweepEnabled`, `Provide.Enabled`, `Provide.DHT.Interval`, and `Provide.Strategy`.

Control flow: `TestProvideStatAllMetricsDocumented` starts a sweep provider, runs `provide stat --all`, extracts metric names, reads `docs/provide-stats.md`, and verifies every emitted metric has documentation. Basic tests check brief output labels and offline rejection. Flag tests cover `--all`, `--compact` requiring `--all`, compact two-column layout, individual section flags, and combined sections. Legacy-provider tests assert old stats fields and rejection of sweep-specific flags. Format tests assert JSON shape has either `Sweep` or `Legacy`. Integration tests verify adding content increases scheduled keys and that all documented strategies render stats. Disabled-config tests distinguish `Provide.Enabled=false` from `Provide.DHT.Interval=0`.

State and persistence: stats reflect live daemon provider state, including queues, schedule, operations, and strategy-dependent scheduling. No on-disk persistence is directly asserted here, but the schedule must update after content is added.

Dependencies and integration points: depends on provider subsystem selection, stats command formatting, documentation file layout, JSON field names, and daemon online mode.

Risks and test signals: the metric-documentation parser contains a suspicious indent condition that currently skips all indented lines because both branches use `HasPrefix`; if fixed, it will enforce docs more strongly. Other risks are timing around schedule updates and exact label churn. Failures signal provider stats unavailable, flag validation drift, undocumented metric additions, or legacy/sweep output shape regressions.
