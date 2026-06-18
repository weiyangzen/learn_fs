# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/LongsCheckpointFormat.java

## Purpose
`LongsCheckpointFormat` reads and renders checkpoints containing a sequence of longs.

## Important APIs, Types, And Functions
`createReader` returns `LongsCheckpointReader`, which validates type `LONGS`. `nextLong` reads longs until `EOFException`, returning `Optional.empty`. `parseToHumanReadable` prints one long per line.

## Control Flow, State, Dependencies, Risks, And Tests
The persisted format is a type header followed by zero or more Java data-stream longs. Dependencies are `CheckpointInputStream`, `Optional`, and Guava preconditions. Risks include partial trailing long being treated as EOF, no count/checksum at this layer, and wrong-type rejection. Tests should cover empty and multi-long checkpoints, partial trailing bytes, wrong type, and render output.
