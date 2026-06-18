# sources/distributed-fs/beegfs-go/rst/sync/internal/config/config.go

## Purpose
This file defines the top-level BeeSync application configuration consumed by `configmgr`.

## Important APIs, Types, and Functions
`AppConfig` combines mount point, work-manager config, BeeRemote client config, worker server config, logging config, and developer options. It implements `configmgr.Configurable` through `NewEmptyInstance`, `UpdateAllowed`, and `ValidateConfig`.

## Control Flow
`NewEmptyInstance` returns a fresh config object for unmarshalling. `UpdateAllowed` currently permits all config updates because dynamic BeeRemote-provided settings are handled outside `configmgr`. `ValidateConfig` rejects nonpositive worker counts and nonpositive active work queue sizes.

## State and Persistence Behavior
The file defines configuration shape only. Persistence paths are contained inside nested work-manager config and are validated by the components that open them.

## Dependencies and Integration Points
It integrates `common/configmgr`, `common/logger`, `sync/internal/beeremote`, `sync/internal/server`, and `sync/internal/workmgr`. `cmd/beegfs-sync/main.go` uses it as the config manager schema.

## Risks and Edge Cases
Validation is intentionally minimal and does not check mount point, TLS file existence, DB path validity, or server address syntax. Because `UpdateAllowed` returns nil, future config-manager dynamic updates could be accepted even if components cannot apply them unless additional validation is added.

## Test Signals
No direct tests cover this config type. Startup paths indirectly rely on `ValidateConfig`, but invalid config combinations beyond worker counts and queue size are not tested here.
