# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/composition_test.go

Purpose: tests reader/cursor composition contracts used by daily replay drain and startup validation.

Important tests: frozen cursor keys remain included in `MinTsNs`; `Snapshot` returns a deep copy not affected by later caller or cursor mutations; `Restore` replaces rather than merges state and clears frozen flags; `Reader.Run` validates shard id, nil events channel, and empty buckets path before subscribing.

Control flow/state: cursor tests mutate multiple action-key positions and freeze state. Reader validation cases call `Run` with nil client under a bounded context to prove validation happens before client use.

Dependencies/integration: uses lifecycle `ActionKey` and `ShardCount`. These contracts feed subscription resume points, checkpoint persistence, and bounded worker startup behavior.

Risks: if freezes were excluded from min position, a blocked action could be skipped or replayed incorrectly. If restore merged, stale cursor positions would survive rebootstrap. If validation regressed, nil clients could panic or hang.

Test signals: strong safety coverage for resume-point selection and input validation, complementing basic cursor and reader tests.
