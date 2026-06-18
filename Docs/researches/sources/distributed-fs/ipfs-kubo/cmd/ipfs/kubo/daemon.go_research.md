# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon.go

## Purpose
This file defines and implements `ipfs daemon`, the long-running Kubo node process that opens the repo, migrates if necessary, builds the core node, starts plugins, RPC API, gateway, optional FUSE mounts, optional GC, libp2p gateway, metrics, MFS remote pinning, version checks, and graceful shutdown.

## Important APIs, Types, And Functions
The central command is `daemonCmd`; `daemonFunc` is the orchestration entrypoint. Helper functions include `defaultMux`, `serveHTTPApi`, `serveHTTPGateway`, `serveTrustlessGatewayOverLibp2p`, `mountFuse`, `checkFusePath`, `maybeRunGC`, `merge`, `YesNoPrompt`, `printVersion`, `printLibp2pPorts`, `rewriteMaddrToUseLocalhostIfItsAny`, and `startVersionChecker`.

## Control Flow
Startup injects Prometheus/OpenTelemetry metrics, prints version, manages fd limits, optionally initializes a repo, opens/migrates the repo, loads config, validates AutoConf/private network constraints, constructs routing, sets agent suffix, creates `core.IpfsNode`, starts plugins, binds API and gateway listeners, mounts FUSE if requested, runs GC, starts libp2p gateway and MFS pinning, marks readiness, then fans in long-running error channels until shutdown.

## State And Persistence Behavior
It owns the fsrepo lock, config reads/writes, API/gateway address files, repo migrations, blockstore/datastore state, pinsets, network connections, metrics registrations, FUSE mounts, systemd readiness notifications, and daemon lifecycle. Deferred cleanup closes the node, plugins, mounts, listeners, and migration fetchers.

## Dependencies And Integration Points
It integrates almost every runtime subsystem: config, fsrepo, migrations, libp2p routing, AutoTLS/private network checks, corehttp API/gateway, socket activation, Prometheus/OTel, plugins, FUSE, GC, remote pinning, systemd notification, and version detection.

## Risks And Test Signals
Risks include startup ordering, listener readiness races, fatal config deprecations, private network routing leaks, global metric registration panics, shutdown hangs, and many asynchronous goroutines. Signals are daemon startup text, API/gateway address files, WebUI URL, "Daemon is ready", metrics endpoint, successful shutdown, and integration tests around daemon behavior.
