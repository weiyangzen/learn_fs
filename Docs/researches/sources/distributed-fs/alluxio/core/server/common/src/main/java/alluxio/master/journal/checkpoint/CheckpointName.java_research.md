# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointName.java

## Purpose
`CheckpointName` enumerates stable names for checkpointed master components.

## Important APIs, Types, And Functions
The enum values cover file system, block, meta, table, inode stores, mount table, path properties, scheduler, snapshot id, and noop components.

## Control Flow, State, Dependencies, Risks, And Tests
Names are persisted in compound checkpoints as strings and in per-component checkpoint file names. The file comment states names should never change to preserve backward compatibility. There are no external dependencies. Risks include renaming/removing enum constants breaking old checkpoints, adding duplicate conceptual names, and `valueOf` failures in compound readers for unknown future names. Tests should cover old checkpoint compatibility, file-name usage, and new component additions requiring enum updates.
