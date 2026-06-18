# sources/control-plane/rook/pkg/daemon/ceph/client/status.go

This file models and queries `ceph status` JSON, then provides health predicates used by upgrades and filesystem orchestration.

The core data structures are `CephStatus`, `HealthStatus`, `CheckMessage`, `MonMap`, `MgrMap`, `OsdMap`, `PgMap`, `Fsmap`, and nested entries matching Ceph status JSON. `Status()` uses `NewCephCommand` for normal admin command execution. `StatusWithUser()` finalizes explicit `ceph status --format json` args and returns richer command-output errors. `IsClusterClean()` compiles an optional PG-state regex, calls `isClusterClean()`, and reports a message plus boolean. The default regex accepts active clean, deep scrubbing, snaptrim, and snaptrim-wait variants. `getMDSRank()` finds an MDS by filesystem name while tolerating standby cases. `MdsActiveOrStandbyReplay()` allows active, standby-replay, and standby states. `IsCephHealthy()` treats `HEALTH_WARN` and `HEALTH_OK` as acceptable. `MuteHealthWarning()` best-effort mutes sticky health warnings.

State is read from Ceph and health mutes are persisted in Ceph monitor state. Dependencies are Ceph command wrappers, JSON decoding, regex matching, and shared logging.

Risks include partial modeling of status JSON, using array index rather than rank value in `getMDSRank()`, and broad health acceptance of warnings. `status_test.go` validates JSON unmarshalling, PG clean logic, MDS rank lookup, health-state decisions, and non-panicking mute behavior.
