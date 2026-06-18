# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointInputStream.java

## Purpose
`CheckpointInputStream` reads the checkpoint type header before exposing checkpoint payload bytes.

## Important APIs, Types, And Functions
The constructor extends `DataInputStream`, reads a leading long, converts it through `CheckpointType.fromLong`, and stores the type. `getType` returns the parsed checkpoint type.

## Control Flow, State, Dependencies, Risks, And Tests
Every checkpoint payload begins after the type id. EOF while reading the id is treated as an old/invalid checkpoint and throws an `IllegalStateException` with upgrade guidance. Dependencies include `RuntimeConstants`, `CheckpointType`, and Java data streams. Risks include consuming the header irreversibly, unknown ids failing hard, and old Alluxio 1.x checkpoints requiring explicit upgrade. Tests should cover valid types, EOF, unknown ids, and wrapping behavior with compressed/digest streams.
