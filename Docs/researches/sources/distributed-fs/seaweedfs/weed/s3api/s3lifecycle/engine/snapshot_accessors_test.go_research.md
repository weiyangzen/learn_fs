# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/snapshot_accessors_test.go

Purpose: tests read-side snapshot accessors and activation transitions used by router, dispatcher, and scheduler.

Important coverage: `OriginalDelayGroups` exposes per-kind delay groups and excludes scan-only actions; `PredicateActions` includes tag-sensitive actions and stays empty for non-tag rules; `DateActions` contains expiration-date actions and is empty for non-date rules; `MarkActive` ignores unknown keys and flips known compiled actions; `BucketActionKeys` covers all compiled kinds for a bucket.

Control flow/state: snapshots are produced via `Compile`; prior states set modes/activation. Tests validate defensive-copy style APIs indirectly by inspecting returned maps/slices without mutating internals here.

Dependencies/integration: uses `MinTriggerAge`, `RuleHash`, `RuleActionKinds`, and `PriorState`. These accessors are the public surface other packages should use instead of internal maps.

Risks: `OriginalDelayGroups` exclusion of scan-only actions depends on compile indexing policy. If scan-only routing later changes, these tests must be revisited. Date actions are keyed by action key and store the rule date verbatim.

Test signals: strong signal for index completeness and mode-sensitive exposure, especially all-kind bucket action coverage needed by `MatchPath`.
