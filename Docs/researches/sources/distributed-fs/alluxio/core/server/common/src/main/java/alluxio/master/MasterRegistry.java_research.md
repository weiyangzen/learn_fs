# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/MasterRegistry.java

## Purpose
`MasterRegistry` is the typed registry for Alluxio master services.

## Important APIs, Types, And Functions
It extends `Registry<Master, Boolean>` and only provides a public constructor.

## Control Flow, State, Dependencies, Risks, And Tests
The inherited registry owns dependency ordering, startup, shutdown, and server lists; the Boolean option is passed to master `start` to indicate primary mode. It does not persist data. Dependencies are `Registry` and `Master`. Risks are all behavior being inherited, so changes in `Registry` affect master orchestration. Tests should focus on registry integration: dependency ordering, Boolean propagation, server enumeration for backups, and thread-safety inherited from `Registry`.
