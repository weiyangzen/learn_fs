<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/diag.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/diag.go

## Purpose

Defines diagnostic commands for daemon health and low-level datastore inspection/mutation.

## Important APIs, Types, and Functions

`DiagCmd` registers `sys`, `cmds`, `profile`, `datastore`, and `healthy`. `diagHealthyCmd` probes shutdown state and built-in DAG resolution. `openDiagDatastore` opens the repo datastore and mounts provider keystore datastores. `diagDatastoreGetCmd`, `diagDatastorePutCmd`, and `diagDatastoreCountCmd` expose raw datastore get/put/count. Result types include `diagDatastoreGetResult` and `diagDatastoreCountResult`.

## Control Flow

Health checks fail if shutdown has started, then resolve and fetch a built-in empty UnixFS directory CID. Datastore commands are `NoRemote` and guarded by `DaemonNotRunning`; they open fsrepo directly, mount extra provider stores if present, perform the requested datastore operation, and close all stores. `get --hex` formats a hex dump; otherwise it writes raw bytes.

## State and Persistence Behavior

`healthy` is read-only. `diag datastore get/count` are read-only. `diag datastore put` writes raw bytes to a datastore key and syncs it, which can directly mutate repo internals while the daemon is stopped.

## Dependencies and Integration Points

Uses shutdown state, CoreAPI DAG/path operations, fsrepo, datastore/mount/query packages, node provider keystore mounting, and command text encoders.

## Risks and Edge Cases

Datastore commands are explicitly debugging-only and can corrupt repo state if misused. Opening repo while daemon runs is blocked by `DaemonNotRunning`. Health probe isolates DAG/blockstore pipeline but does not prove network health.

## Test Signals

No direct tests in this subset. Useful tests include shutdown health failure, missing/corrupt probe behavior, datastore not-found messages, hex output, put sync errors, and provider keystore mount inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/diag.go -->
