# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestAfsCheckPath.java

## Purpose
`TestAfsCheckPath` is a targeted unit test for `AbstractFileSystem.checkPath()` port validation. It ensures paths with no port, the default port, and the same non-default port are accepted, while a mismatched port is rejected.

## Important APIs, Types, And Functions
The test defines `DEFAULT_PORT = 1234`, `OTHER_PORT = 4321`, and a private `DummyFileSystem` extending `AbstractFileSystem`. The dummy constructor calls `super(uri, "dummy", true, DEFAULT_PORT)` and overrides `getUriDefaultPort()`. Required abstract filesystem methods are stubbed with empty behavior because only `checkPath()` is under test.

## Control Flow
Each test constructs a URI and a `DummyFileSystem`, then calls `afs.checkPath()` with a `Path` URI. Three tests expect success: no explicit port, explicit default port, and matching non-default port. `testCheckPathWithDifferentPorts()` wraps the call in `assertThrows(InvalidPathException.class)`.

## State And Persistence Behavior
There is no filesystem persistence. The dummy implementation returns null or false for storage methods and exists only to expose `AbstractFileSystem` path validation logic.

## Dependencies And Integration Points
The test integrates with `AbstractFileSystem`, `Path`, `InvalidPathException`, URI parsing, and the default-port normalization rules used by all abstract filesystem implementations.

## Risks
The dummy methods are deliberately nonfunctional, so adding assertions beyond `checkPath()` would be invalid. Coverage is limited to host/port equivalence and does not test scheme mismatch, authority case, paths without authority, or IPv6 authority formatting.

## Test Signals
Passing tests show that `AbstractFileSystem.checkPath()` treats default ports as equivalent and rejects paths whose explicit port differs from the filesystem URI port.
