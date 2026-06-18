# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/add_migrations.go

## Purpose
This file caches or pins migration binaries fetched during repo migration into the running IPFS node.

## Important APIs, Types, And Functions
`addMigrations` dispatches by fetcher type. `addMigrationFiles` adds downloaded local files through UnixFS. `addMigrationPaths` connects to a temporary migration peer and pins or reads fetched IPFS paths. `ipfsGet` reads a UnixFS file to force block import.

## Control Flow
Multi-fetchers are flattened. IPFS fetchers provide peer info and paths; HTTP fetchers scan `migrations.DownloadDirectory`. Files are added one by one, optionally pinned. IPFS paths require connecting to the migration peer first.

## State And Persistence Behavior
It mutates the node blockstore and optionally pinset. It reads migration download directories and network-fetched paths but does not manage cleanup itself.

## Dependencies And Integration Points
It integrates fsrepo migration fetchers, `coreapi`, UnixFS add/get, swarm connect, remote pinning of migration artifacts, and daemon migration flow.

## Risks And Test Signals
Risks include unknown fetcher types, empty path/address errors, file descriptor cleanup, and expensive reads. Signals are printed "Added migration file" messages and successful cached/pinned artifacts.
