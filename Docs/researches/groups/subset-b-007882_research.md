# subset-b-007882 Research

Grouped research for SeaweedFS S3 lifecycle files in `sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle`. Each section is source-tree aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/sibling_lister.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/sibling_lister.go

Purpose: implements `filerSiblingLister`, the `router.SiblingLister` adapter backed by a Seaweed filer client. It centralizes lifecycle queries over `.versions/<key>/` and bare-key null versions so dispatcher/router code does not reimplement version-layout knowledge.

Important APIs: `NewFilerSiblingLister`, `Survivors`, `ListVersions`, `LookupNullVersion`, and `LookupVersion`. `Survivors` counts version siblings with a limit of two, tracks a lone entry only when exactly one version exists, and checks the bare key as a null version. `ListVersions` pages with size 1024 and filters out directories, nil attributes, and entries without `ExtVersionIdKey`. `LookupNullVersion` returns the bare regular file or explicit directory-key marker plus an `explicit` null-version flag. `LookupVersion` maps version id to `v_<id>`.

Control flow and state: stateless except for `client` and `bucketsPath`. It normalizes bucket paths with `strings.TrimSuffix` and uses `util.NewFullPath` for trailing-slash object keys. Not-found is collapsed to nil/zero results for expected races; other filer errors propagate.

Dependencies/integration: depends on `filer_pb.SeaweedList`, `filer_pb.LookupEntry`, `s3_constants` version metadata keys, and router survivor interfaces. It feeds expired delete-marker and noncurrent-version routing decisions.

Risks: pagination relies on `lastName` progressing; version entries with absent/empty version ids are intentionally ignored. Directory-key markers must be distinguished from plain directories to avoid treating prefixes as null versions. NotFound behavior depends on `LookupEntry` normalization.

Test signals: `sibling_lister_test.go` covers not-found collapse, lone-entry clearing after count > 1, directory-key null markers, list filtering, 1024+ pagination, explicit null detection, `v_` lookup prefixing, and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/sibling_lister.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/sibling_lister_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/sibling_lister_test.go

Purpose: tests `filerSiblingLister` with a fake filer implementing the small `ListEntries` and `LookupDirectoryEntry` surface used by the lister.

Important helpers/APIs: `fsListStream`, `fsFakeFiler`, `newFakeFiler`, `newLister`, and `versionEntry`. The fake models sorted list responses, `StartFromFileName` pagination, first-`Recv` not-found errors, one-shot injected transport errors, and tree-backed lookup.

Control flow and state: tests build an in-memory directory tree keyed by filer directory path. `Survivors` cases exercise version count capping and null bare-key lookup. `ListVersions` cases force missing containers, filtered invalid entries, a 1030-entry pagination boundary, and list errors. `LookupNullVersion` and `LookupVersion` cases drive regular files, explicit null ids, directory-key markers, plain directories, not-found collapse, and transport errors.

Dependencies/integration: imports filer protobufs, `s3_constants`, gRPC stream interfaces, and testify. It documents expectations the router and dispatcher rely on when determining sole survivors and version identities.

Risks: fake behavior must stay close to real filer semantics, especially not-found surfacing from stream `Recv` and exclusive `StartFromFileName`; drift could hide production bugs. The embedded client intentionally panics on unexpected method use.

Test signals: this is the signal source. It confirms safety for hard-delete races, directory marker handling, version filtering, pagination ordering, and non-NotFound error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/sibling_lister_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/due_at.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/due_at.go

Purpose: computes lifecycle action due times without deciding whether to dispatch now. It is used by reader/bootstrap paths to classify entries as pending or immediately eligible.

Important APIs: `DaysToDuration(days int)` converts lifecycle day thresholds through `util.LifeCycleInterval`, allowing s3tests builds to shrink days. `ComputeDueAt(rule, kind, info)` returns a zero `time.Time` when inputs, status, filters, object shape, or action kind do not allow a due time.

Control flow: after nil/status/filter checks, it switches by `ActionKind`. Abort MPU uses initiation mod time plus abort days. Expired delete marker returns marker mod time only for current sole-survivor markers. Current expiration days/date apply only to latest non-marker objects. Noncurrent days use `SuccessorModTime` or fall back to `ModTime`. Pure newer-noncurrent returns successor/mod time immediately when count-only rules apply.

State/persistence: pure function; no mutation. The due time depends on `ObjectInfo` state including latest flag, delete marker flag, version count, mtime, successor mtime, and MPU status.

Dependencies/integration: shares `filterMatches` from `evaluate.go`; depends on rule action shape and `util.LifeCycleInterval`.

Risks: `ActionKindNewerNoncurrent` due time is only a scheduling hint; final deletion still needs current ranking. Missing successor stamps fall back to legacy mtime, which can be less exact.

Test signals: `due_at_test.go` pins expiration days/date, sole-survivor delete-marker gating, undeclared kind zero, wrong object shape zero, noncurrent delete markers, successor mtime, filters, disabled rules, and MPU initiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/due_at.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/due_at_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/due_at_test.go

Purpose: verifies `ComputeDueAt` as the scheduling-time companion to `EvaluateAction`.

Important test cases: expiration by days adds `DaysToDuration`; expiration by date returns the configured date; expired delete marker returns zero when not the sole survivor; undeclared action kinds and wrong object shapes return zero. Noncurrent delete markers are treated as normal noncurrent versions under noncurrent-days rules. Noncurrent due time prefers `SuccessorModTime`; filters and disabled status suppress due times; MPU init records use abort days from initiation mtime.

Control flow coverage: tests exercise every switch branch with both positive and negative paths. They also show that kind/action matching is strict; asking an abort-MPU kind of an expiration-only rule cannot synthesize a due time.

State/persistence behavior: no persisted state, but tests model `ObjectInfo` fields that come from entry metadata, sibling scans, and bootstrap expansion.

Dependencies/integration: reuses `mustTime` from `evaluate_test.go` and lifecycle rule structs.

Risks: because `DaysToDuration` is build-tag-scaled, tests compare to that helper rather than hard-coded 24h days. Missing direct test for pure `ActionKindNewerNoncurrent` due time is a residual gap, though evaluation tests cover deletion behavior.

Test signals: strong branch-level signal for due-date math and filter/status gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/due_at_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/compile.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/compile.go

Purpose: compiles per-bucket lifecycle rules into immutable snapshot indexes of per-action `CompiledAction` objects.

Important APIs/types: `CompileInput`, `PriorState`, `CompileOptions`, `Engine.Compile`, and `rulePredicateSensitive`. Each lifecycle XML rule expands through `s3lifecycle.RuleActionKinds` into one `ActionKey` per action kind, scoped by bucket and rule hash. `PriorState` carries durable bootstrap and mode state.

Control flow: `Compile` applies default bootstrap lookback, creates a fresh `Snapshot`, builds a `BucketIndex` per input bucket, hashes each rule, decides or preserves each action mode, determines activation, and fills indexes: bucket action keys, all actions map, date actions, original delay groups, and predicate-sensitive actions. Date actions are considered active without bootstrap rendezvous; event-driven actions require `BootstrapComplete`. Durable non-unspecified mode wins over recomputation.

State/persistence: atomically increments snapshot id and stores the snapshot in `Engine.current`. Prior states reflect durable lifecycle state; compile itself does not persist.

Dependencies/integration: uses `RuleHash`, `RuleActionKinds`, `MinTriggerAge`, `EventLogHorizon` via `decideMode`, and `SmallDelay`. Output indexes feed router matching, daily replay, bootstrap, and scheduler date scans.

Risks: duplicate `CompileInput.Bucket` entries overwrite bucket indexes. Preserving prior mode prevents accidental re-promotion, but stale modes require explicit repair. Active gating is subtle: indexes include inactive event-driven actions so `MarkActive` can work without recompilation.

Test signals: engine tests cover multi-action expansion, retention degradation, mode preservation, scan-at-date, disabled rules, cross-bucket identical rule hashes, delay group deduplication, and atomic snapshot swap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/compile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/compile_helpers_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/compile_helpers_test.go

Purpose: direct unit coverage for `rulePredicateSensitive`, the helper that decides whether a rule should be indexed for predicate-change events.

Important cases: nil rules return false defensively; rules with no `FilterTags` return false; non-nil but empty tag maps return false; populated tag filters return true.

Control flow/state: no runtime state. The helper is intentionally tag-only: size filters are immutable after object write, while tags in the entry `Extended` metadata can change without resetting object mtime.

Dependencies/integration: imports `s3lifecycle.Rule` and testify. `Compile` uses this helper to fill `CompiledAction.PredicateSensitive` and append action keys to `Snapshot.predicateActions` when mode is event-driven.

Risks: if future mutable predicates are added beyond tags, this helper must be updated or predicate-change routing will miss them. Conversely, over-classifying immutable predicates would waste routing work but not usually affect correctness.

Test signals: focused branch coverage for a small but routing-sensitive helper; broader match tests verify `PredicateActions` and `MatchPredicateChange` behavior end to end.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/compile_helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/engine.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/engine.go

Purpose: defines the core engine and snapshot data model used by lifecycle routing.

Important APIs/types: `Engine`, `New`, `Snapshot`, `BucketIndex`, `CompiledAction`, `SnapshotID`, `Action`, `AllActions`, `OriginalDelayGroups`, `PredicateActions`, `DateActions`, `BucketVersioned`, `BucketActionKeys`, and `MarkActive`. `CompiledAction` contains the rule pointer, bucket, action key, delay, predicate sensitivity, mode, and atomic active bit.

Control flow: `New` installs an empty snapshot. `Snapshot` returns the atomically current snapshot. Accessors either return direct immutable data (`Action`, `AllActions`) or defensive copies for mutable maps/slices. `MarkActive` flips the atomic active state when a key exists and silently ignores stale keys.

State/persistence: in-memory snapshots are swapped atomically by compile. The only post-compile mutation is per-action `engineState`, used to activate event-driven actions after durable bootstrap completion.

Dependencies/integration: used by router, dispatcher, daily-run partitioning, and tests. `ActionKey` from `s3lifecycle` is the identity key.

Risks: `AllActions` returns the internal sorted slice by design, so callers must not mutate. Bucket/action maps are otherwise shared read-only. `MarkActive` races are deliberately tolerated but only affect the current snapshot object receiving the call.

Test signals: snapshot accessor tests cover defensive copies, activation, unknown-key no-op, bucket versioned flags, action key coverage, all-action enumeration, and monotonic snapshot ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/engine.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/engine_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/engine_test.go

Purpose: exercises the compile path and core snapshot semantics.

Important helpers/tests: `ruleExpDays` builds enabled expiration rules. Tests verify single-action compile, multi-action sibling expansion, bootstrap-pending indexing but inactive status, retention gating, unbounded retention, sibling-specific degradation, durable prior mode preservation, expiration date date-actions, disabled rule behavior, `MarkActive`, cross-bucket action-key scoping, snapshot atomic swap, and delay-group deduplication across many buckets.

Control flow coverage: tests walk through mode decisions and index population, especially the difference between indexed-but-inactive event-driven actions and active scan-at-date actions. Multi-action tests ensure one XML rule produces independent action keys and delay groups.

State/persistence behavior: `PriorState` stands in for durable bootstrap/mode state. Tests confirm persisted scan-only state survives compile and does not accidentally become active.

Dependencies/integration: ties `RuleHash`, `RuleActionKinds`, `DaysToDuration`, and `CompileOptions` together.

Risks/gaps: retention-gate tests skip under shortened s3tests day units, so production-day behavior depends on normal build coverage. Tests use internal maps, which is appropriate for package-level invariants.

Test signals: strong regression coverage for identity scoping, mode preservation, delay grouping, and atomic snapshot replacement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/engine_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/hashes.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/hashes.go

Purpose: computes stable hashes that daily replay cursors use to detect rule-content changes and retention partition flips.

Important APIs: `ReplayContentHash`, `PromotedHash`, and `MaxEffectiveTTL`. Internal helpers include `hashItem`, `sortHashItems`, `hashWriter`, and `effectiveTTL` from `views.go`.

Control flow: both hash functions collect non-disabled replay-eligible actions, sort by rule hash, action kind, and bucket, then write varint-tagged fields into SHA-256. `ReplayContentHash` includes bucket, rule hash, action kind, and effective TTL, but intentionally ignores whether an action is currently replay or walk. `PromotedHash` includes replay-eligible actions that would land in walk for a retention window. `MaxEffectiveTTL` scans active replay-eligible actions and returns the maximum effective TTL.

State/persistence: pure computations over snapshots. Their outputs are intended for persisted cursor metadata; mismatches trigger recovery paths.

Dependencies/integration: depends on `Snapshot.actions`, `RuleMode`, `ActionKind`, and replay partition rules. It must match `RulesForShard` membership exactly for promoted actions.

Risks: hash schema changes affect persisted cursors. `PromotedHash` with retention 0 treats all replay-eligible actions as promoted, matching safe walk-only behavior. Disabled and walker-only actions are excluded from replay content.

Test signals: `hashes_test.go` verifies empty cases, partition independence, content edits, rule reorder stability, disabled/walker exclusion, promoted hash flips both directions, agreement with `RulesForShard`, and max TTL behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/hashes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/hashes_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/hashes_test.go

Purpose: validates replay and promotion hash contracts used by cursor recovery logic.

Important tests: nil/walker-only snapshots produce empty replay hashes; replay content hash remains stable when retention partition changes; TTL edits change replay content; rule order does not affect hash; walker-only and disabled additions are excluded. Promotion tests cover empty when nothing is promoted, replay-to-walk and walk-to-replay changes, stability for unchanged partition, and membership agreement with `RulesForShard`. Max TTL tests cover nil/empty, max across replay actions, replay-view-only behavior, and inactive action exclusion.

Control flow/state: tests build snapshots through `buildSnapshotForViews`, ensuring compile indexes and prior bootstrap state are realistic. Hashes are compared as value outputs; no mutation.

Dependencies/integration: depends on `RulesForShard` and `DaysToDuration` to prove hash semantics align with runtime partitioning.

Risks/gaps: `PromotedHash_MatchesRulesForShardWalkMembership` checks non-empty/hash behavior rather than decoding hash contents, which is expected for SHA outputs but means exact item list is inferred from partition setup.

Test signals: high-value regression signal for recovery correctness; accidental ordering drift, disabled-rule inclusion, or retention predicate mismatch should fail these tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/hashes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match.go

Purpose: matches lifecycle meta-log events and bootstrap paths against compiled snapshot indexes.

Important APIs/types: `EventShape`, `Event`, `Snapshot.MatchOriginalWrite`, `MatchPredicateChange`, `MatchPath`, plus helpers `filterMatching`, `prefixMatches`, and `filterAllows`. Engine-level `Event` deliberately avoids filer protobuf dependency.

Control flow: original-write matching requires shape `EventShapeOriginalWrite`, selects keys by exact delay group, then filters by active bit, bucket, prefix, size/tags, and action-specific shape gates. Predicate-change matching requires shape `EventShapePredicateChange` and only considers tag-sensitive actions. `MatchPath` is bucket/path oriented; with nil event it applies prefix only, and with an event it also applies filters.

State/persistence: read-only over snapshot indexes and action active bits. No persistence.

Dependencies/integration: used by reader/router/bootstrap dispatch paths. Size filters are strict greater-than/less-than; tag filters are ANDed exact matches.

Risks: action-shape gates are easy to miss. Abort MPU must only match MPU init events. Expired delete marker must be latest and delete marker. `MatchPath` with nil event intentionally skips tag/size because bootstrap may fetch/evaluate live state later.

Test signals: match tests cover delay routing, prefix/filter gates, activation after `MarkActive`, predicate sensitivity, bucket scoping, action-shape gates, nil/wrong-shape inputs, and bootstrap prefix-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match_helpers_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match_helpers_test.go

Purpose: focused tests for low-level match helpers and edge cases that broader match tests might obscure.

Important coverage: `prefixMatches` allows empty prefixes, accepts exact prefixes, rejects non-matching or shorter paths. `filterAllows` tests no-filter fast path, strict size greater-than and less-than boundaries, zero-size filter disabled behavior, required tag presence, multi-tag AND behavior, and size+tag conjunction. Additional match cases cover nil/wrong event shapes, delay mismatch, no tag-sensitive predicate actions, unknown buckets, nil-event prefix-only `MatchPath`, event-provided filter gates, bucket scoping, AbortMPU requiring MPU init, and expired delete marker requiring marker+latest.

Control flow/state: uses compiled snapshots from helper builders so internal indexes are realistic. No persistent state.

Dependencies/integration: imports lifecycle rules, action keys, and testify. It documents router expectations for the event-driven matching surface.

Risks/gaps: tests directly use package internals, which is desirable for helper contracts but can require updates when implementation is intentionally refactored.

Test signals: excellent boundary coverage for filter semantics; catches off-by-one size filter changes, cross-bucket leakage, and shape-gate regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match_helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match_test.go

Purpose: integration-style unit tests for public snapshot matching APIs.

Important helpers/tests: `activeAll` creates prior states activating every compiled action; `sortedKeys` stabilizes kind comparison. Tests verify delay-group routing for different expiration days, prefix filtering, inactive bootstrap actions becoming routable after `MarkActive`, AbortMPU matching only MPU init events, predicate changes matching only tag-sensitive rules, bootstrap `MatchPath` seeing all active actions in a multi-action rule, prefix mismatch exclusion, and nil-event `MatchPath` returning prefix-only matches despite tag filters.

Control flow/state: tests go through `Engine.Compile`, so bucket indexes, delay groups, predicate actions, and active bits are populated by production code. They distinguish event-driven matching from bootstrap/walker matching.

Dependencies/integration: integrates `RuleActionKinds`, `RuleHash`, `DaysToDuration`, and snapshot match APIs.

Risks: expected delay values must use `DaysToDuration`; hard-coded 24h values would break under s3tests build scaling. Tests validate per-kind expansion and activation, key to multi-action rule correctness.

Test signals: strong runtime-surface signal that compiled indexes route to the correct action keys and respond to activation flips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/mode.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/mode.go

Purpose: defines lifecycle rule execution modes and the default mode decision policy.

Important APIs/types: `RuleMode` enum, `String`, and `decideMode`. Modes include unspecified, event-driven, scan-at-date, scan-only, disabled, and pending-bootstrap. String rendering is used in logs/metrics/state bridges.

Control flow: `decideMode` returns disabled for nil or disabled rules. Expiration-date actions are scan-at-date. Other actions are event-driven unless `MetaLogRetention` is positive and less than `EventLogHorizon(rule, kind) + bootstrapLookbackMin`, in which case they become scan-only. Retention 0 means unbounded and never gates.

State/persistence: no persistence directly, but `RuleMode` mirrors durable protobuf lifecycle state. Compile may preserve durable prior mode over `decideMode`.

Dependencies/integration: calls `s3lifecycle.EventLogHorizon` and consumes `ActionKind`. Scheduler, daily replay, and bootstrap use modes to select event-driven, date-scan, or scan-only paths.

Risks: retention math is sensitive to build-tag day scaling and lookback margin. Unknown enum values stringify as `unspecified`, which avoids empty labels but can hide unexpected durable values if not logged with numeric context elsewhere.

Test signals: `mode_test.go` covers nil/disabled, date mode, unbounded retention, retention threshold boundaries, lookback effects, zero horizon, and string rendering including unknown values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/mode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/mode_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/mode_test.go

Purpose: validates default rule mode decisions and mode string labels.

Important tests: nil and disabled rules resolve to disabled; expiration-date actions resolve to scan-at-date; unbounded retention uses event-driven; horizons within retention remain event-driven; horizons exceeding retention become scan-only; bootstrap lookback can push a rule across the threshold; zero horizons do not gate; `RuleMode.String` renders documented names and falls back to `unspecified`.

Control flow/state: direct calls to `decideMode` isolate mode policy from compile indexing. Tests use lifecycle rules with expiration days and dates plus retention/lookback durations.

Dependencies/integration: depends on `EventLogHorizon`, `DaysToDuration`, and `SmallDelay` semantics.

Risks/gaps: package-private testing is appropriate, but durable prior mode preservation is covered in compile tests rather than here. Time-scaling build tags can affect threshold expectations, so tests choose durations through lifecycle helpers.

Test signals: good policy-level signal for retention gate regressions and operator-visible string labels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/mode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/snapshot_accessors_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/snapshot_accessors_test.go

Purpose: tests read-side snapshot accessors and activation transitions used by router, dispatcher, and scheduler.

Important coverage: `OriginalDelayGroups` exposes per-kind delay groups and excludes scan-only actions; `PredicateActions` includes tag-sensitive actions and stays empty for non-tag rules; `DateActions` contains expiration-date actions and is empty for non-date rules; `MarkActive` ignores unknown keys and flips known compiled actions; `BucketActionKeys` covers all compiled kinds for a bucket.

Control flow/state: snapshots are produced via `Compile`; prior states set modes/activation. Tests validate defensive-copy style APIs indirectly by inspecting returned maps/slices without mutating internals here.

Dependencies/integration: uses `MinTriggerAge`, `RuleHash`, `RuleActionKinds`, and `PriorState`. These accessors are the public surface other packages should use instead of internal maps.

Risks: `OriginalDelayGroups` exclusion of scan-only actions depends on compile indexing policy. If scan-only routing later changes, these tests must be revisited. Date actions are keyed by action key and store the rule date verbatim.

Test signals: strong signal for index completeness and mode-sensitive exposure, especially all-kind bucket action coverage needed by `MatchPath`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/snapshot_accessors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/views.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/views.go

Purpose: constructs per-run snapshot views for daily replay, walking, and recovery without mutating the base compiled snapshot.

Important APIs: package-level `SetCurrentEngine`/`CurrentSnapshot`, `Snapshot.RulesForShard`, and `RecoveryView`. Internal helpers include `cloneAction`, `newView`, `isReplayKind`, and `effectiveTTL`.

Control flow: `CurrentSnapshot` reads a global engine pointer, returning nil if not registered. `RulesForShard` partitions non-disabled actions: replay-eligible kinds (`ExpirationDays`, `NoncurrentDays`, `AbortMPU`) go to replay when `ttl > 0 && ttl <= retentionWindow`, otherwise walk; walker-only kinds always go to walk. Replay clones are active and force `ModeEventDriven`; walk clones preserve base mode. Retention 0 routes replay kinds to walk. `RecoveryView` clones every non-disabled action active, preserving mode.

State/persistence: only package-level atomic engine pointer is mutable. Views share immutable base indexes/rules but clone `CompiledAction` active state, preventing view mutations from leaking back.

Dependencies/integration: daily-run uses replay/walk partitions; recovery walker uses forced-active view. TODO notes production wiring must call `SetCurrentEngine`.

Risks: `shardID` is reserved and currently ignored, so every shard receives every rule. Shared bucket/index maps require callers not to mutate base snapshot internals. Missing engine registration yields nil and short-circuit behavior.

Test signals: `views_test.go` covers current-engine access, partition membership, scan-only promotion, replay rehabilitation of scan-only mode, disabled exclusion, clone independence, zero-retention safety, and recovery view activation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/views.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/views_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/views_test.go

Purpose: validates snapshot view construction for replay, walk, and recovery paths.

Important helpers/tests: `buildSnapshotForViews` compiles active snapshots. Tests cover nil/current engine behavior, nil snapshot partitioning, replay membership for day-based/MPU actions, walk-only kinds, multi-action rules split across replay/walk, scan-only promotion when TTL exceeds retention, replay forcing `ModeEventDriven` on rehabilitated scan-only actions, disabled exclusion, clone independence from base actions, zero retention routing replay kinds to walk, recovery activation of inactive actions, preserving scan-at-date mode, disabled exclusion in recovery, and recovery clone independence.

Control flow/state: tests inspect per-view action maps and active bits. They deliberately mutate clone active state to prove atomics are not shared with base actions.

Dependencies/integration: ties `RulesForShard`, `RecoveryView`, compile prior state, and retention windows together.

Risks/gaps: `shardID` is not behaviorally tested because current implementation ignores it by design. Package-level current engine tests save and restore global pointer to avoid cross-test pollution.

Test signals: strong coverage for safe partitioning and recovery semantics, especially retention loss and mode rehabilitation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/views_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/evaluate.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/evaluate.go

Purpose: evaluates whether a lifecycle rule action should fire for an object at a specific time.

Important API: `EvaluateAction(rule, kind, info, now) EvalResult` and helper `filterMatches`. It returns `ActionNone` for nil/disabled/nonmatching inputs and maps eligible actions to lifecycle dispatcher actions such as delete object, delete version, expire delete marker, and abort MPU.

Control flow: the function filters by status and rule filters, suppresses all non-abort actions for MPU-init records, then switches by action kind. Current expiration days/date require latest non-marker objects and due time. Expired object delete marker requires current sole-survivor marker. Noncurrent days require non-latest plus due time; if keep-N is configured, nil index or too-new index suppresses deletion. Pure newer-noncurrent is count-only and requires an index at or beyond keep count.

State/persistence: pure function over `Rule`, `ObjectInfo`, and `now`. It relies on caller-provided version ranking and successor timestamps derived from metadata or sibling scans.

Dependencies/integration: used by router/bootstrap/daily-run dispatch before issuing deletes. `filterMatches` implements prefix, strict size, and tag-equality filters and is also used by `ComputeDueAt`.

Risks: nil `NoncurrentIndex` is safety-critical; guessing would delete retained versions. MPU-init records have `IsLatest=false`, so the explicit guard prevents noncurrent actions from freezing dispatcher cursors on empty version ids.

Test signals: `evaluate_test.go` covers branch boundaries, multi-action independence, filters, noncurrent markers, keep-N semantics, nil-index safety, and MPU guard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/evaluate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/evaluate_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/evaluate_test.go

Purpose: comprehensive tests for lifecycle action evaluation.

Important helpers/tests: `idx` creates noncurrent indexes and `mustTime` parses fixed UTC times. Tests cover nil/disabled no-ops, expiration-day boundary at due time, undeclared action kinds, multi-action sibling independence, expiration date, expired delete marker sole-survivor behavior, noncurrent delete markers under noncurrent days, successor-time due math, fallback to mod time, keep-N nil-index no-op, pure newer-noncurrent count thresholds, combined noncurrent days plus keep-N, abort MPU boundaries, prefix/tag/size filters, empty prefix, and MPU init suppression for noncurrent kinds.

Control flow/state: tests populate `ObjectInfo` fields representing live and bootstrap-derived state. Boundary checks use `now.Before(due)` semantics, so equality fires.

Dependencies/integration: covers `filterMatches` through public evaluation and shares `DaysToDuration` for build-tag-safe day math.

Risks/gaps: tests do not inspect `RuleID` for every firing action, but boundary and action mapping are well covered. The nil-index safety tests document intentional no-op behavior for pointer migration and ranking gaps.

Test signals: high-confidence behavioral signal for deletion eligibility and safety gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/evaluate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/event_log_horizon.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/event_log_horizon.go

Purpose: computes the meta-log history horizon required to safely drive a lifecycle action from events.

Important API: `EventLogHorizon(rule, kind) time.Duration`. It returns day-derived horizons for expiration days, noncurrent days, and abort MPU; `SmallDelay` for pure count/immediate kinds (`NewerNoncurrent` without days and expired delete marker); zero for nil, undeclared, or date-based actions.

Control flow: the switch is per-action-kind rather than per-rule. Multi-action rules do not share the largest threshold across siblings, allowing independent retention gating.

State/persistence: pure function. Its output influences compile-time mode selection and may indirectly affect durable rule mode through scan-only degradation.

Dependencies/integration: uses `DaysToDuration` and `SmallDelay`; consumed by `decideMode` in the engine.

Risks: returning too small a horizon can make event-driven replay miss old due events; returning too large a horizon can unnecessarily degrade actions to scan-only. Count-only actions use `SmallDelay` because they depend on immediate state changes rather than long object age.

Test signals: `event_log_horizon_test.go` verifies per-action independence, newer-noncurrent count-only behavior, paired noncurrent-days behavior, expired marker small delay, date zero, nil zero, and undeclared zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/event_log_horizon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/event_log_horizon_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/event_log_horizon_test.go

Purpose: verifies action-specific event-log horizon calculations.

Important tests: multi-action rules produce independent horizons for expiration days, abort MPU, and noncurrent days; expiration-date returns zero. Pure newer-noncurrent returns `SmallDelay`, but when paired with noncurrent days the newer-noncurrent kind is not considered declared and returns zero while noncurrent-days carries the day horizon. Expired delete marker returns `SmallDelay`. Nil rules and undeclared kinds return zero.

Control flow/state: direct pure-function calls over rule structs. No persistent state.

Dependencies/integration: validates values used by engine mode decisions and retention gate tests.

Risks/gaps: tests assume action-kind expansion logic elsewhere will not create a `NewerNoncurrent` action when noncurrent days is set; that is tested in action-kind/rule tests outside this work item.

Test signals: good focused coverage for a small function whose incorrect output could silently alter event-driven versus scan-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/event_log_horizon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/final_cleanup_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/final_cleanup_test.go

Purpose: gap-filling tests for small lifecycle helpers before broader integration work.

Important tests: `TestActionKind_StringUnspecifiedDefault` pins unknown/default action kind rendering to `"unspecified"`. `TestHashExtended_DirectFromLifecyclePackage` verifies nil/empty extended maps hash to empty bytes, non-empty maps hash to bytes, and multi-key maps hash stably regardless of insertion order.

Control flow/state: tests pure helpers; no persistence. The hash test forces the sort path by using multiple keys.

Dependencies/integration: uses testify and calls `HashExtended`, whose output is used by identity-CAS lifecycle delete requests. Action kind strings feed metrics labels and operator-readable logs.

Risks: this file is named as cleanup rather than function-specific, so future maintainers may overlook it when changing `ActionKind.String` or `HashExtended`. It intentionally supplements broader tests in other packages.

Test signals: small but valuable coverage for default branches and deterministic CAS witness hashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/final_cleanup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/identity.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/identity.go

Purpose: provides canonical hashing of an entry's `Extended` metadata for lifecycle identity compare-and-swap.

Important API: `HashExtended(ext map[string][]byte) []byte`. It returns nil for empty maps. For non-empty maps, it sorts keys and feeds SHA-256 with length-prefixed key and value bytes.

Control flow/state: pure deterministic function. Length prefixes prevent ambiguous concatenation collisions such as a forged single tag matching a multi-tag map. Sorting removes Go map iteration nondeterminism.

Dependencies/integration: used by both the lifecycle worker capturing schedule-time identity and the server refetching live entry identity. The bytes must match exactly across both sides for CAS validation.

Risks: any format change is a compatibility change for in-flight lifecycle delete witnesses. Returning nil for empty maps must remain consistent with server-side interpretation of no extended metadata. It hashes all `Extended` keys, not only object tags, so unrelated metadata changes can intentionally invalidate a scheduled delete.

Test signals: `final_cleanup_test.go` covers nil/empty, non-empty, and insertion-order stability; broader identity tests in s3api are referenced by comments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/identity.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder.go

Purpose: supplies reusable test builders for `reader.Event` fixtures that look like production filer meta-log events.

Important APIs: `EventOption`, `WithSize`, `WithModTime`, `WithTtlSec`, `WithVersionID`, `WithExtended`, `WithChunks`, `WithOldSize`, `WithOldChunks`, `WithOldModTime`, `WithBootstrapVersion`, `WithShardID`, `NewCreate`, `NewDelete`, `NewUpdate`, `MetaLogClock`, and `leafOf`.

Control flow: constructors populate only new, old, or both entries depending on create/delete/update shape, derive shard id from bucket/key, set default mtime to event timestamp, and then apply options in order. Generic options target `NewEntry` when present or `OldEntry` for deletes; `WithOld*` options target old entry on updates. `leafOf` strips trailing slashes and parent prefixes to mimic filer entry names.

State/persistence: test-only. `MetaLogClock` holds mutex-protected current time and step to produce monotonic fixture timestamps.

Dependencies/integration: uses filer protobufs, S3 extended metadata constants, lifecycle shard hashing, and reader bootstrap version structures. These helpers are used by lifecycle router/dispatcher/daily-run tests.

Risks: if fixture shape diverges from real filer events, tests may become misleading. Options silently no-op on missing target entries by design.

Test signals: eventbuilder tests cover constructor shapes, leaf names, shard derivation, option targeting and override order, old-entry branches, bootstrap version attachment, panic safety, and concurrent clock uniqueness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder_old_entry_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder_old_entry_test.go

Purpose: fills coverage for event builder options when events have only `OldEntry` or need bootstrap-version attachment.

Important tests: `WithModTime`, `WithTtlSec`, `WithVersionID`, `WithExtended`, and `WithChunks` apply to `OldEntry` on delete events. `WithBootstrapVersion` attaches the same pointer to create, delete, and update events. `TestEventOption_NoPanicOnEmptyEvent` applies all options to a degenerate empty event and verifies entry-targeting options do not allocate entries while bootstrap-version still sets the event field.

Control flow/state: confirms generic option fall-through branches in `eventbuilder.go`. No persistence; uses constructed `reader.Event`.

Dependencies/integration: imports filer chunks, S3 constants, and `reader.BootstrapVersion`.

Risks: these tests document no-op behavior that callers may depend on when composing options. If future options allocate missing entries, test fixture semantics would change.

Test signals: focused branch coverage for delete/old-entry paths that create/update-oriented tests would miss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder_old_entry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder_test.go

Purpose: validates the main lifecycle event fixture builder surface.

Important tests: create/delete/update constructors populate the expected entry sides and default mtimes; nested and directory keys produce filer-style leaf names; shard id matches production `ShardID`. Options set size, mtime, TTL, version id, extended keys, chunks, shard override, old-entry size/chunks/mtime on update, and no-op behavior of old options on create. Later options override earlier ones. `MetaLogClock` tests default/custom step, peek behavior, and concurrent unique timestamps.

Control flow/state: tests option application order and target-entry selection. Clock tests exercise mutex-protected mutable state.

Dependencies/integration: uses filer protobuf chunks, S3 constants, lifecycle shard hashing, and testify.

Risks/gaps: builder tests do not validate every downstream router interpretation, but they ensure fixtures are shaped correctly for those tests. Concurrent clock test requires race detector for full data-race signal, but uniqueness/deadlock is checked normally.

Test signals: broad confidence that test fixtures mirror production event anatomy, especially for directory keys and update old/new separation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/fakeserver.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/fakeserver.go

Purpose: provides a thread-safe fake implementation of the internal S3 lifecycle gRPC server for tests.

Important APIs/types: `Outcome`, constructors `Done`, `NoopResolved`, `RetryLater`, `Blocked`, `SkippedObjectLock`, `FakeLifecycleServer`, `NewFakeLifecycleServer`, `Queue`, `SetDefault`, `SetError`, `Recorded`, and `LifecycleDelete`.

Control flow: the fake holds per-request-key FIFO outcome queues keyed by `(bucket, objectPath, versionId)`, a default outcome, optional transport error, and deep-copied received requests. `LifecycleDelete` checks `err` first and short-circuits without recording, records a cloned request, handles nil request via default, pops queued outcomes, or falls back to default.

State/persistence: all mutable state is in-memory protected by a mutex. `Recorded` returns deep copies so callers cannot mutate internal history.

Dependencies/integration: implements `s3_lifecycle_pb.SeaweedS3LifecycleInternalServer` and uses protobuf `proto.Clone`. It allows worker/router tests to exercise gRPC boundary outcomes without a real S3 server.

Risks: mid-call mutation ordering is intentionally undefined around concurrent `Queue`/`SetDefault`; tests should configure before calls when ordering matters. Nil request handling is defensive rather than production-normal.

Test signals: fakeserver tests cover default, FIFO queues, key isolation, version scoping, delimiter collision avoidance, error short-circuit, recording order, deep copies, nil requests, and concurrent calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/fakeserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/fakeserver_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/fakeserver_test.go

Purpose: validates the lifecycle fake server used by component tests.

Important tests: default outcome is DONE; queued outcomes pop FIFO and then default applies; queues are isolated by bucket/object/version; delimiter-containing key components do not collide because map key is a struct; transport errors short-circuit before recording and can be cleared; recorded requests preserve order; recorded slices and requests are deep copies; nil requests use default; concurrent calls complete without errors and record all requests.

Control flow/state: tests mutate fake queues, default, error state, and recorded snapshots to confirm locking and copy boundaries. Concurrency test uses 64 goroutines.

Dependencies/integration: uses lifecycle protobuf outcomes and requests plus testify.

Risks/gaps: concurrent test checks completion and length, with race detector needed to prove absence of data races. It does not assert deterministic order under concurrency, which is appropriate.

Test signals: strong confidence that tests using this fake can model dispatcher outcomes, transport failures, blocked/retry paths, and request recording without cross-test contamination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/fakeserver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/min_trigger_age.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/min_trigger_age.go

Purpose: returns the day-style minimum trigger age for a specific lifecycle action kind.

Important API: `MinTriggerAge(rule, kind) time.Duration`. It returns `DaysToDuration` for expiration days, noncurrent days, and abort MPU when the matching threshold is positive; otherwise zero.

Control flow: nil rule returns zero. Date, count-only, expired delete marker, undeclared kinds, and non-positive thresholds all return zero. The function is per-kind and does not choose a maximum across a multi-action rule.

State/persistence: pure function. Output is stored in compiled actions as `Delay` and used by safety-scan cadence and original-write delay grouping.

Dependencies/integration: used by `engine.Compile`, snapshot delay groups, and tests; depends on `DaysToDuration`.

Risks: returning a non-zero delay for date/count/immediate actions would incorrectly place them in original-write delay groups. Returning zero for declared day actions would over-poll or mispartition dispatch paths.

Test signals: `min_trigger_age_test.go` covers per-kind values, undeclared kind zero, date-only zero, and nil rule zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/min_trigger_age.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/min_trigger_age_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/min_trigger_age_test.go

Purpose: validates per-kind trigger-age extraction.

Important tests: a rule with expiration days, noncurrent days, and abort MPU returns each respective `DaysToDuration`; expiration date, newer noncurrent, and expired delete marker return zero. Asking a kind not set on the rule returns zero. Date-only rules and nil rules return zero.

Control flow/state: direct pure-function tests; no mutable state.

Dependencies/integration: uses `DaysToDuration` for build-tag-safe expectations and `mustTime` for date-only setup.

Risks/gaps: tests cover positive thresholds but not explicitly zero/negative threshold fields for day kinds; production XML parsing likely prevents negative values, and zero is implicitly covered by date/kind-not-set cases.

Test signals: focused branch-level signal for compile delay grouping and safety-scan cadence inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/min_trigger_age_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/noncurrent_since.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/noncurrent_since.go

Purpose: parses the explicit noncurrent-since timestamp stamped on entries when a version is demoted.

Important API: `SuccessorFromEntryStamp(entry *filer_pb.Entry) time.Time`. It reads `s3_constants.ExtNoncurrentSinceNsKey` from `Entry.Extended`, parses it as Unix nanoseconds, and returns zero for nil, missing, empty, unparseable, or non-positive values.

Control flow/state: pure parser over entry metadata. It prefers the demotion stamp over legacy successor mtime derivation because the stamp records the actual demotion time and is immune to later sibling mtime edits.

Dependencies/integration: used by router and bootstrap walker to populate `ObjectInfo.SuccessorModTime` consistently. Depends on filer protobuf entries and S3 constants.

Risks: callers must fall back correctly on zero for legacy entries. A malformed stamp silently becomes zero, so bad writers degrade precision instead of failing routing. Nanosecond values must be decimal strings.

Test signals: `noncurrent_since_test.go` covers nil/missing/empty/invalid/non-positive values, positive nanosecond round-trip, and ordering preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/noncurrent_since.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/noncurrent_since_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/noncurrent_since_test.go

Purpose: direct coverage for `SuccessorFromEntryStamp`, the canonical parser for noncurrent demotion timestamps.

Important tests: nil entry, missing extended map, and empty map return zero. Nil, empty, and non-numeric raw values return zero. `"0"` and negative values return zero. A positive nanosecond string round-trips to `time.Unix(0, ns)`. Ordered nanosecond stamps produce non-decreasing parsed times.

Control flow/state: pure parser tests using fixed constants to avoid wall-clock monotonic artifacts. No persistence.

Dependencies/integration: imports filer protobufs and `ExtNoncurrentSinceNsKey`.

Risks/gaps: tests do not cover overflow values explicitly; `strconv.ParseInt` errors would fall into invalid/zero behavior. The ordering test uses fixed consecutive ns values, which is appropriate for parser properties.

Test signals: strong branch coverage for safe fallback semantics shared by router and bootstrap walker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/noncurrent_since_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/composition_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/composition_test.go

Purpose: tests reader/cursor composition contracts used by daily replay drain and startup validation.

Important tests: frozen cursor keys remain included in `MinTsNs`; `Snapshot` returns a deep copy not affected by later caller or cursor mutations; `Restore` replaces rather than merges state and clears frozen flags; `Reader.Run` validates shard id, nil events channel, and empty buckets path before subscribing.

Control flow/state: cursor tests mutate multiple action-key positions and freeze state. Reader validation cases call `Run` with nil client under a bounded context to prove validation happens before client use.

Dependencies/integration: uses lifecycle `ActionKey` and `ShardCount`. These contracts feed subscription resume points, checkpoint persistence, and bounded worker startup behavior.

Risks: if freezes were excluded from min position, a blocked action could be skipped or replayed incorrectly. If restore merged, stale cursor positions would survive rebootstrap. If validation regressed, nil clients could panic or hang.

Test signals: strong safety coverage for resume-point selection and input validation, complementing basic cursor and reader tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/composition_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/cursor.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/cursor.go

Purpose: maintains per-action meta-log cursor positions for one lifecycle shard.

Important APIs/type: `Cursor`, `NewCursor`, `MinTsNs`, `Get`, `Advance`, `Freeze`, `Unfreeze`, `IsFrozen`, `Snapshot`, and `Restore`. State maps `ActionKey` to last fully resolved timestamp and separately tracks frozen keys.

Control flow: `Advance` is monotonic, ignores non-positive timestamps, and is a no-op for frozen keys. `Freeze` pins a key and seeds its position if unset. `MinTsNs` returns the minimum state value or zero if empty. `Snapshot` copies positions only; frozen state is persisted elsewhere. `Restore` replaces the map and clears freezes.

State/persistence: in-memory, mutex-protected. `Snapshot`/`Restore` are the persistence boundary used by persisters and startup.

Dependencies/integration: reader uses `MinTsNs` as `SubscribeMetadata.SinceNs`. Dispatcher/blocker flows freeze actions on blocked outcomes.

Risks: long freezes can exceed meta-log retention; comments note operator blocker resolution is needed. Persisted snapshots do not include frozen flags, so callers must reapply them from blocker records.

Test signals: cursor and composition tests cover empty/min, monotonic advance, zero ignore, freeze/unfreeze, freeze-on-unset seeding, snapshot deep copy, restore replacement, and frozen min inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/cursor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/cursor_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/cursor_test.go

Purpose: baseline unit tests for cursor position and freeze behavior.

Important tests: empty cursor min is zero; `Advance` is monotonic and ignores backward/equal moves; zero/negative advances are ignored; min across keys returns the smallest timestamp; freeze blocks advances until unfreeze; freeze on unset seeds the position; snapshot/restore round-trips values and does not restore frozen flags.

Control flow/state: tests directly mutate cursor state through public methods and inspect positions via `Get`/`MinTsNs`.

Dependencies/integration: uses lifecycle action keys and action kinds; supports reader resume and dispatcher freeze logic.

Risks/gaps: concurrency behavior is protected by locks but not stress-tested here; composition tests cover deep copy/restore replacement, and race coverage would require running with `-race`.

Test signals: good branch coverage for the core cursor API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/cursor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/event_predicates_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/event_predicates_test.go

Purpose: direct tests for `reader.Event` create/delete predicates.

Important tests: a populated `NewEntry` with nil `OldEntry` is create; populated `OldEntry` with nil `NewEntry` is delete; update events with both entries are neither; degenerate events with neither entry are neither.

Control flow/state: pure predicate checks over event entry fields. No persistence.

Dependencies/integration: uses filer protobuf entries. Dispatcher/router paths use these predicates to select create/delete/update routing behavior.

Risks: classifying updates as creates or deletes would route pointer transitions incorrectly. Classifying empty metadata events could trigger spurious lifecycle dispatch.

Test signals: small but important direct coverage for routing-critical predicates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/event_predicates_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/log_startup_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/log_startup_test.go

Purpose: executes `Reader.LogStartup` branches for compile-time and panic-safety coverage.

Important tests: single-shard `ShardID` logging; shard-predicate/range logging; explicit `StartTsNs` overriding cursor min; cursor min fallback when `StartTsNs` is zero.

Control flow/state: tests do not assert log output, only that the helper runs through each branch without panic. Cursor state may be empty.

Dependencies/integration: `LogStartup` writes through SeaweedFS glog. It is used by worker startup for a one-line resume summary.

Risks/gaps: no log-capture assertion means format changes are not pinned; this is acceptable because behavior is diagnostic, not functional. The tests mainly prevent branch rot and nil dereferences.

Test signals: light coverage for logging paths and resume-position selection in log context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/log_startup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/persister.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/persister.go

Purpose: defines cursor persistence contract and ships an in-memory implementation for tests.

Important APIs/types: `Persister` interface with `Load` and `Save`, `InMemoryPersister`, and `NewInMemoryPersister`. Contract: unknown shards load as empty maps; save replaces prior state atomically; callers serialize concurrent saves for the same shard in production.

Control flow: in-memory load locks, copies stored shard state into a new map, and returns it. Save locks, copies input state, and replaces the shard entry.

State/persistence: `InMemoryPersister` stores `map[int]map[ActionKey]int64` under a mutex. It is test-only; filer-backed persistence lives elsewhere.

Dependencies/integration: used by reader/daily-run tests as a cursor checkpoint double. Action keys are lifecycle identities.

Risks: production implementation must match deep-copy and replace-not-merge semantics or stale cursor positions and caller mutations could corrupt resume state. Context arguments are accepted but in-memory implementation does not inspect cancellation.

Test signals: persister tests cover unknown loads, round-trip, input/output copy isolation, replace semantics, shard isolation, empty save clearing, and concurrent save/load behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/persister.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/persister_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/persister_test.go

Purpose: verifies `InMemoryPersister` obeys the documented cursor persistence contract.

Important tests: unknown shard loads return non-nil empty maps; save/load round-trips; save copies input; load returns a copy; save replaces instead of merging; shard ids are isolated; saving an empty map clears prior state; concurrent save/load operations do not deadlock and are intended for race-detector validation.

Control flow/state: tests mutate input and loaded maps after calls to prove copy boundaries. Concurrent test launches paired goroutines across four shard ids.

Dependencies/integration: uses lifecycle action keys and context. This in-memory double underpins other lifecycle tests.

Risks/gaps: in-memory implementation ignores context cancellation, acceptable for tests but not a production persistence pattern. Concurrency test checks completion; data-race detection requires `go test -race`.

Test signals: strong signal for deep-copy and replace semantics, which are critical for cursor correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/persister_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/reader.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/reader.go

Purpose: subscribes to the filer metadata log, filters events to lifecycle bucket/shard scope, and emits `reader.Event` values to downstream routing.

Important APIs/types: `Event`, `BootstrapVersion`, `Reader`, `Run`, `dispatchOne`, `extractBucketKey`, `LogStartup`, plus `Event.IsCreate` and `IsDelete`. `BootstrapVersion` carries walker-derived version ranking/state for noncurrent evaluation.

Control flow: `Run` validates shard/channel/path inputs, computes `SinceNs` from explicit start or cursor min, calls `SubscribeMetadata`, then processes primary and batched events until EOF/error/context/budget. `dispatchOne` skips nil notifications, extracts bucket/key, filters by shard id or predicate, and sends events respecting context cancellation. `extractBucketKey` reconstructs bucket/key from parent path and entry name, handling deletes with `resp.Directory`, bucket-root events, and paths outside `BucketsPath`.

State/persistence: reader itself does not advance/persist cursors; it uses cursor min as subscription start. Event budget bounds one run.

Dependencies/integration: depends on filer protobuf stream, lifecycle shard hashing, and glog. Downstream router/dispatcher consume emitted events and acknowledge actions.

Risks: path normalization around `/buckets` vs `/buckets/`, deletes with empty new parent, and bucket-root events are subtle. Sending to an unbuffered channel can block; context cancellation handles it.

Test signals: reader tests cover path extraction variants, shard filtering, context cancellation, input validation, event predicates, and startup logging branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/reader_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/reader_test.go

Purpose: tests reader path extraction and event dispatch behavior.

Important tests: create path extracts nested bucket/key; top-level object extraction; delete uses old entry; delete with empty new parent falls back to response directory; outside-bucket paths are skipped; bucket root events work with `/buckets/` and bare `/buckets`; `dispatchOne` filters nonmatching shards and emits matching shard events; context cancellation unblocks a send to an unbuffered channel.

Control flow/state: tests call private methods directly within package. They construct filer metadata responses and channels, then inspect emitted `Event` fields and processed counts.

Dependencies/integration: uses filer protobuf metadata response shapes and lifecycle `ShardID`.

Risks/gaps: `Run` streaming loop and batched event handling are not fully fake-stream tested here, though validation is covered in composition tests. Path extraction coverage is strong for known filer shapes.

Test signals: good signal for bucket/key reconstruction and shard gating, both central to avoiding misrouted lifecycle work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/helpers_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/helpers_test.go

Purpose: direct coverage for router helper functions and engine snapshot accessor behavior that larger route tests exercise indirectly.

Important tests: `successorModTimeFromContainer` handles missing/empty/non-numeric/non-positive values and positive seconds. `logicalKeyFromVersionPath`, `isVersionsContainerKey`, and `isVersionFolderPath` classify `.versions` paths. `isDeleteMarkerEntry` only accepts literal `"true"`. `extractTags` extracts only object-tagging-prefixed extended keys and returns nil when none. `hasActiveEventDrivenAction` requires the specific kind to be active and mode event-driven, skipping scan-only and nil actions. Snapshot accessor cross-checks cover bucket versioned flags, bucket action keys, unknown action nil, all actions covering kinds, and monotonic snapshot ids.

Control flow/state: tests combine pure helpers with compiled engine snapshots. They model version path strings, filer extended metadata, and prior state modes.

Dependencies/integration: imports router package internals, filer protobufs, S3 constants, lifecycle types, and engine compile APIs. These helpers support route classification for version folders, delete markers, tag filters, and event-driven eligibility.

Risks: path classification must reject bucket-root `.versions` and malformed version paths to avoid treating infrastructure folders as objects. Literal delete-marker parsing avoids truthy ambiguity. Snapshot helper tests overlap engine tests but document router-facing expectations.

Test signals: strong edge-case signal for version path parsing, tag extraction, active-action checks, and snapshot accessor contracts used by router code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/router/helpers_test.go -->
