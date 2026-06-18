# sources/cloud-native/nydus-snapshotter/config/daemonconfig/fscache.go

Purpose: fscache/EROFS nydusd configuration model and snapshot-specific supplementing.

Flow: `LoadFscacheConfig` reads JSON template and requires non-nil `Config`. `Supplement` fills registry host/repo, computes fscache ID from snapshot ID, sets `ID`, `DomainID`, nested config ID, optional workdir, and metadata bootstrap path. `FillAuth` stores registry token or base64 auth. Dump methods serialize/write JSON.

State/dependencies: reads/writes config files and logs shared-domain warning. Depends on auth and erofs helpers.

Integration points: used when fs driver is `fscache`; config is passed through nydusd APIs rather than always persisted.

Risks/tests: shared `DomainID` behavior depends on kernel >=6.1. No direct tests listed for fscache load/supplement.
