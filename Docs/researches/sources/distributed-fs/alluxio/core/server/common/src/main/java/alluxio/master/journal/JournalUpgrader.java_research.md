# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalUpgrader.java

## Purpose
`JournalUpgrader` is a CLI tool for upgrading UFS journals from Alluxio v0 layout to v1 layout.

## Important APIs, Types, And Functions
`main` parses `-help` and `-journalDirectoryV0`, discovers master names, and runs an `Upgrader` per master. `Upgrader.prepare` recovers/completes v0 logs, formats v1 if needed, and creates checkpoint/log directories. `upgrade` renames the v0 checkpoint and completed logs into v1 sequence-range names after scanning each completed log with `JournalFileParser`.

## Control Flow, State, Dependencies, Risks, And Tests
The upgrade mutates persistent UFS paths: `checkpoint.data`, v0 `completed/log.N`, v1 `checkpoints/0x0-0x...`, and v1 `logs/0xstart-0xend`. Dependencies include v0 `MutableJournal`, v1 `UfsJournal`, `UnderFileSystem`, `ServiceUtils`, CLI parser, and URI utilities. Risks include destructive renames without rollback, assumptions about v0/v1 directories sharing storage, missing logs after checkpoint rename, scanning entire logs to compute ranges, and service-loader master names not matching old journal folders. Tests should use a fake UFS to cover no-checkpoint no-op, checkpoint-only upgrade, multi-log ranges, rename failure, argument parsing, and idempotent reruns.
