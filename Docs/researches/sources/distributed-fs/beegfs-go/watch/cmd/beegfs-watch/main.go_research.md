# sources/distributed-fs/beegfs-go/watch/cmd/beegfs-watch/main.go

## Purpose

This is the BeeWatch daemon entry point. It wires configuration, logging, license verification, metadata event ingestion, subscriber management, dynamic config reloads, pprof, and graceful shutdown into a single process that relays BeeGFS metadata events to configured subscribers.

## Important APIs, Types, And Functions

`main` defines pflags for logging, management gRPC, subscriber handler behavior, hidden developer options, and version output. Build variables `binaryName`, `version`, `commit`, and `buildTime` are set through linker flags. It creates a `configmgr.Manager` over `config.AppConfig`, initializes a common logger, verifies the `io.beegfs.watch` license through `beegrpc.NewMgmtd`, constructs `metadata.New`, constructs `subscribermgr.New`, registers both logger and subscriber manager as config listeners, and starts `metaMgr.Manage`, `sm.Manage`, and `cfgMgr.Manage`.

## Control Flow

Startup order is deliberate: parse config, optionally dump config/version, initialize logging, optionally start pprof, read management TLS/auth files, verify license, initialize the metadata socket and event buffer, initialize subscriber manager, start subscriber handling, then start metadata ingestion last to avoid accepting events before subscribers are ready. Shutdown first cancels metadata ingestion, then waits until `EventBuffer.AllEventsAcknowledged()` or a second signal forces subscriber shutdown, then stops dynamic config and waits on the shared wait group.

## State And Persistence

The daemon itself persists no event state on disk. Event state is in memory in the metadata manager's multi-cursor ring buffer, while subscriber-side acknowledgements can avoid duplicates after reconnects. It reads certificate and auth secret files at startup. Log persistence depends on `logger.Config` and can rotate file logs.

## Dependencies And Integration Points

The command integrates with BeeGFS management gRPC for license checks, BeeGFS metadata through the configured Unix socket, the common config manager for flag/env/TOML precedence, the common logger, `metadata.Manager`, and `subscribermgr.Manager`. The SIGHUP reload behavior is handled by `configmgr.Manage`, while SIGINT/SIGTERM drive shutdown.

## Risks And Test Signals

Startup can block or fail on management connection, TLS/auth file errors, license failure, or metadata socket setup. The shutdown loop can wait indefinitely after the second phase if subscriber disconnect cleanup hangs. Hidden `management.use-http-proxy` and developer pprof options affect network/security posture. There is no direct test file for `main`; behavior is signaled by component tests plus end-to-end daemon startup/shutdown and config reload tests.
