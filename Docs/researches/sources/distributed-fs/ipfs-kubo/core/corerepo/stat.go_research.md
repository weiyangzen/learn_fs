# sources/distributed-fs/ipfs-kubo/core/corerepo/stat.go

## Purpose
Computes repository size and object-count statistics for repo stat APIs.

## Important APIs, Types, and Functions
Defines `SizeStat`, `Stat`, `NoLimit`, `RepoStat`, and `RepoSize`.

## Control Flow and State
`RepoSize` reads config, asks repo for storage usage, parses `Datastore.StorageMax` when configured, or returns `NoLimit`. `RepoStat` calls `RepoSize`, counts every blockstore key from `AllKeysChan`, obtains the best-known fsrepo path, and returns fs-repo version metadata.

## Dependencies and Integration Points
Depends on core node repo/blockstore, fsrepo path/version, humanize byte parsing, and context. Used by repo stat commands/APIs.

## Risks and Test Signals
Risks include expensive full blockstore scans, context cancellation during count, stale best-known repo path, and parse failures for storage max. Tests should cover no-limit, configured limit, storage usage errors, and object count accuracy.
