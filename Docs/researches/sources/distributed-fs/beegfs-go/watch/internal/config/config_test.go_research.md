# sources/distributed-fs/beegfs-go/watch/internal/config/config_test.go

## Purpose

This test file verifies the dynamic update policy for BeeWatch application configuration, specifically that metadata service configuration is immutable after startup.

## Important APIs, Types, And Functions

`TestUpdateAllowed` constructs an initial `AppConfig` with one `metadata.Config`, a variant with the event log path changed, and a variant with an additional metadata service. It asserts `UpdateAllowed` accepts the unchanged config and rejects both metadata changes.

## Control Flow

The test calls `currentConfig.UpdateAllowed(&currentConfig)`, `UpdateAllowed(&newConfig)`, and `UpdateAllowed(&newConfig2)`, using testify `assert.NoError` and `assert.Error` to express the allowed and rejected cases.

## State And Persistence

There is no persistence. Test state is in-memory config structs. The test models runtime reload semantics where metadata changes would require socket and buffer reconstruction.

## Dependencies And Integration Points

It imports `metadata.Config` and `stretchr/testify/assert`. Its signal is consumed by the config package and indirectly protects `main.go`/`configmgr` dynamic reload behavior.

## Risks And Test Signals

Coverage is narrow. It does not test rejection of developer changes, log sink changes, invalid config type, or allowance of subscriber and handler changes. It also does not test `ValidateConfig`. Still, it locks down the most critical invariant: metadata ingestion settings cannot be hot-swapped.
