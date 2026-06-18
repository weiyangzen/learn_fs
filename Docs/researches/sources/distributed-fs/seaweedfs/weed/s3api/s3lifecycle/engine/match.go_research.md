# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/engine/match.go

Purpose: matches lifecycle meta-log events and bootstrap paths against compiled snapshot indexes.

Important APIs/types: `EventShape`, `Event`, `Snapshot.MatchOriginalWrite`, `MatchPredicateChange`, `MatchPath`, plus helpers `filterMatching`, `prefixMatches`, and `filterAllows`. Engine-level `Event` deliberately avoids filer protobuf dependency.

Control flow: original-write matching requires shape `EventShapeOriginalWrite`, selects keys by exact delay group, then filters by active bit, bucket, prefix, size/tags, and action-specific shape gates. Predicate-change matching requires shape `EventShapePredicateChange` and only considers tag-sensitive actions. `MatchPath` is bucket/path oriented; with nil event it applies prefix only, and with an event it also applies filters.

State/persistence: read-only over snapshot indexes and action active bits. No persistence.

Dependencies/integration: used by reader/router/bootstrap dispatch paths. Size filters are strict greater-than/less-than; tag filters are ANDed exact matches.

Risks: action-shape gates are easy to miss. Abort MPU must only match MPU init events. Expired delete marker must be latest and delete marker. `MatchPath` with nil event intentionally skips tag/size because bootstrap may fetch/evaluate live state later.

Test signals: match tests cover delay routing, prefix/filter gates, activation after `MarkActive`, predicate sensitivity, bucket scoping, action-shape gates, nil/wrong-shape inputs, and bootstrap prefix-only behavior.
