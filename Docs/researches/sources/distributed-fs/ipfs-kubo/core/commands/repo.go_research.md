# sources/distributed-fs/ipfs-kubo/core/commands/repo.go

## Purpose

`repo.go` implements `ipfs repo` maintenance commands: garbage collection, stats, version reporting, block verification/remediation, migrations, and local block listing. It is the main command surface for local repository health and lifecycle operations.

## Important APIs, Types, and Functions

`RepoCmd` registers `stat`, `gc`, `version`, `verify`, `migrate`, and `ls`. Output types include `RepoVersion`, `GcResult`, `VerifyProgress`, and internal `verifyResult`. Verification state is modeled by `verifyState` constants for valid, corrupt, removed, remove-failed, healed, and heal-failed blocks. Helpers include `verifyWorkerRun` and `verifyResultChan`.

## Control Flow

`repo gc` calls `corerepo.GarbageCollectAsync`; with `--stream-errors` it emits each removed CID or error and returns a final error if any occurred, otherwise it collects results while optionally suppressing output. `repo stat` either emits only size stats or full repo stats and text-formats sizes with optional human units. `repo verify` builds a validating blockstore over the repo datastore, parses `--drop`, `--heal`, and heal timeout, requires online CoreAPI for healing, streams all keys, and verifies blocks in `runtime.NumCPU()*2` workers. Corrupt blocks are reported, optionally deleted, and optionally re-fetched via `api.Block().Get`. The command aggregates outcomes and returns non-zero errors when corruption is only detected or remediation fails. `repo version` emits the supported fs-repo version. `repo migrate` is local-only/repo-direct: it reads current repo version, validates downgrade permission, runs hybrid migrations to a target version, and prints migration progress/errors directly.

## State and Persistence Behavior

`gc` deletes unpinned blocks from local storage. `verify` is read-only by default, but `--drop` deletes corrupt blocks and `--heal` deletes then attempts network refetch. `migrate` mutates repository layout/version and can downgrade only with explicit permission. `stat` and `version` are read-only.

## Dependencies and Integration Points

Dependencies include Kubo corerepo, fsrepo, migrations, old command context, CoreAPI block access, Boxo validating blockstore, path/CID types, humanize formatting, and concurrency primitives. It integrates with pinning/GC invariants, repo locks/migration tooling, and `refs local`.

## Risks and Test Signals

Risks are high because GC, verify drop/heal, and migrate are destructive. Tests should cover GC streaming and silent/quiet encoders, stats size-only/human output, verify corrupt detection, drop success/failure, heal online gating and timeout, worker cancellation, final exit-error rules, version quiet output, migration no-op, downgrade rejection/allowance, migration failure messaging, and not opening the repo through daemon paths before migrations acquire locks.
