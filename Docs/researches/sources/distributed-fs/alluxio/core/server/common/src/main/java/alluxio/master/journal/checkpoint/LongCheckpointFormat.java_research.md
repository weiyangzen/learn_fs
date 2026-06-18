# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/LongCheckpointFormat.java

## Purpose
`LongCheckpointFormat` reads and renders checkpoints containing a single long.

## Important APIs, Types, And Functions
`createReader` returns `LongCheckpointReader`, which validates type `LONG`. `getLong` reads the long from the checkpoint stream. `parseToHumanReadable` prints the value.

## Control Flow, State, Dependencies, Risks, And Tests
The persisted format is a type header followed by one Java data-stream long. Dependencies are `CheckpointInputStream` and Guava `Preconditions`. Risks include EOF if the payload is missing, extra bytes not detected by `getLong`, and wrong-type failure. Tests should cover valid values, negative/large values, EOF, wrong type, and human-readable output.
