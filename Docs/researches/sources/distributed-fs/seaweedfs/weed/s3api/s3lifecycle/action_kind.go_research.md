# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/action_kind.go

Purpose: defines lifecycle action identity and stable action-kind expansion for compiled S3 lifecycle rules.

Important APIs/types: `ActionKey` scopes actions by `Bucket`, `RuleHash`, and `ActionKind`. `ActionKind` enum includes expiration by days/date, noncurrent expiration, newer-noncurrent retention, abort MPU, and expired delete marker. `ActionKind.String()` returns stable on-disk leaf names. `RuleActionKinds(rule *Rule)` expands one XML rule into deterministic action kinds.

Control flow: `RuleActionKinds` appends action kinds when the matching rule field is active. `NewerNoncurrentVersions` is only emitted as `ActionKindNewerNoncurrent` when `NoncurrentVersionExpirationDays` is absent, because together they define one noncurrent expiration action. The order is deterministic: expiration days, expiration date, expired delete marker, noncurrent/newer-noncurrent, abort MPU.

State and persistence behavior: `ActionKind.String()` is load-bearing for `/etc/s3/lifecycle/<bucket>/<rule_hash>/<action_kind>/` paths and cursor/dispatcher state. Renaming strings would orphan existing lifecycle state.

Dependencies and integration points: consumed by lifecycle engine, router, dispatcher proto conversion, bootstrap walker, daily-run partitions, metrics labels, and filer persistence paths.

Risks: adding a new action kind requires updates in proto mapping (`dispatch.go`, `walker_dispatcher.go` via shared helper), engine evaluation, routing, persistence naming, metrics expectations, and tests. The implicit iota values mirror proto concepts but are not themselves wire values.

Test signals: `action_kind_test.go` pins single-action and multi-action expansion, subsumption of `NewerNoncurrentVersions`, nil/empty behavior, and stable string names.
