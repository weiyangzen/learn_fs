# sources/control-plane/rook/pkg/daemon/ceph/client/filesystem_test.go

Purpose: provides broad unit coverage for CephFS JSON models, filesystem deletion, MDS control helpers, standby polling, subvolume discovery, and standby replay settings.

Important test cases: marshal tests verify `CephFilesystem` and `CephFilesystemDetails` struct tags. `TestFilesystemRemove` simulates `fs get`, `fs rm`, pool lookup, pool stats, and pool deletion to ensure metadata and data pools are removed when preservation is disabled. `TestFailAllStandbyReplayMDS` covers failing only `up:standby-replay` daemons and error propagation. `TestGetMdsIdByRank` covers success plus missing fs dump, missing rank mapping, and missing info mapping. `TestGetMDSDump`, `TestFSHasStandby`, and `TestWaitForNoStandbys` cover MDS dump parsing and polling behavior. `TestListSubvolumeGroups` and `TestListSubvolumesInGroup` cover empty/multiple/error cases. `TestAllowStandbyReplay` verifies both `allow_standby_replay` and `standby_count_wanted`.

Control flow and dependencies: tests use mock executors with JSON fixtures, `AdminTestClusterInfo()`, short timeouts, and package helpers from pool code during filesystem removal. They rely on standard flags being appended after command-specific args.

Risks and coverage gaps: the test file exercises many failure paths, but does not cover `CreateFilesystem()`, `AddDataPoolToFilesystem()` EINVAL idempotency, `SetNumMDSRanks()`, `WaitForActiveRanks()`, `FailFilesystem()`, subvolume snapshot listing, or pending clone listing. Polling tests use very short intervals/timeouts, which keeps tests fast but can be sensitive to scheduler timing.
