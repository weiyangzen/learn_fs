# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/views.go

Purpose: constructs per-run snapshot views for daily replay, walking, and recovery without mutating the base compiled snapshot.

Important APIs: package-level `SetCurrentEngine`/`CurrentSnapshot`, `Snapshot.RulesForShard`, and `RecoveryView`. Internal helpers include `cloneAction`, `newView`, `isReplayKind`, and `effectiveTTL`.

Control flow: `CurrentSnapshot` reads a global engine pointer, returning nil if not registered. `RulesForShard` partitions non-disabled actions: replay-eligible kinds (`ExpirationDays`, `NoncurrentDays`, `AbortMPU`) go to replay when `ttl > 0 && ttl <= retentionWindow`, otherwise walk; walker-only kinds always go to walk. Replay clones are active and force `ModeEventDriven`; walk clones preserve base mode. Retention 0 routes replay kinds to walk. `RecoveryView` clones every non-disabled action active, preserving mode.

State/persistence: only package-level atomic engine pointer is mutable. Views share immutable base indexes/rules but clone `CompiledAction` active state, preventing view mutations from leaking back.

Dependencies/integration: daily-run uses replay/walk partitions; recovery walker uses forced-active view. TODO notes production wiring must call `SetCurrentEngine`.

Risks: `shardID` is reserved and currently ignored, so every shard receives every rule. Shared bucket/index maps require callers not to mutate base snapshot internals. Missing engine registration yields nil and short-circuit behavior.

Test signals: `views_test.go` covers current-engine access, partition membership, scan-only promotion, replay rehabilitation of scan-only mode, disabled exclusion, clone independence, zero-retention safety, and recovery view activation.
