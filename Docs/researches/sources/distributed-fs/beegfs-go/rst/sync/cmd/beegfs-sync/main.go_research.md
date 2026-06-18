# sources/distributed-fs/beegfs-go/rst/sync/cmd/beegfs-sync/main.go

## Purpose
This file is the BeeSync daemon entrypoint. It parses configuration, initializes logging and BeeGFS client access, starts the BeeRemote client, starts the local work manager, exposes the worker-node gRPC server, and coordinates shutdown.

## Important APIs, Types, and Functions
Global build variables define version metadata. `capabilities` advertises `registry.FeatureFilterFiles`. `main` defines all CLI flags, config/env precedence help, version/dump-config/profiling options, mount-point checks, signal handling, client/server/manager construction, and shutdown ordering.

## Control Flow
The program parses flags, optionally prints version or config, initializes `configmgr`, logger, CTL logging, and the BeeGFS mount provider, then sets up signal cancellation. It checks the BeeGFS client `sysBypassFileAccessCheckOnMeta` setting when available. It creates a BeeRemote client, starts `workmgr.NewAndStart`, creates and serves the worker-node server, blocks on server error or OS signal, then stops server, work manager, and Remote client in order.

## State and Persistence Behavior
The entrypoint configures default persistent DB paths for the work journal and job store under `/var/lib/beegfs/sync`. It does not directly write job state, but it enables pprof, logging rotation, and runtime config initialization. It writes no commits or research state.

## Dependencies and Integration Points
It integrates pflag, `common/configmgr`, `common/logger`, registry capabilities, CTL/procfs BeeGFS access, `sync/internal/beeremote`, `sync/internal/config`, `sync/internal/server`, and `sync/internal/workmgr`.

## Risks and Edge Cases
Fatal startup errors terminate the process. Dynamic config updates are not handled here beyond initial config manager setup and BeeRemote-provided runtime config through the worker server. The procfs mount setting check is warning-only if the parameter is unavailable, preserving backward compatibility but reducing enforcement on older clients. pprof is exposed on localhost port when enabled.

## Test Signals
No direct tests cover `main.go`. Its dependencies are tested at lower layers, but CLI flag wiring, config precedence, shutdown ordering, procfs validation, and pprof setup are not directly covered in this subset.
