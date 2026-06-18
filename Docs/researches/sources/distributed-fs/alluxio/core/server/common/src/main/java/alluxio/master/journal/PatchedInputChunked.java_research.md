# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/PatchedInputChunked.java

## Purpose
`PatchedInputChunked` works around Kryo EOF handling for compound checkpoint reads.

## Important APIs, Types, And Functions
It extends Kryo `InputChunked` and overrides `fill` to translate a `KryoException` with message `Buffer underflow.` into `-1`, while rethrowing other exceptions.

## Control Flow, State, Dependencies, Risks, And Tests
The class has no additional state or persistence; it affects how Kryo chunked streams signal EOF while reading persisted compound checkpoints. Dependencies are Kryo `InputChunked` and `KryoException`. Risks include matching on exception message text, future Kryo behavior changes, and hiding real truncation as EOF if the same message is reused. Tests should read valid compound checkpoints to EOF, feed truncated chunks, and verify non-underflow Kryo exceptions still propagate.
