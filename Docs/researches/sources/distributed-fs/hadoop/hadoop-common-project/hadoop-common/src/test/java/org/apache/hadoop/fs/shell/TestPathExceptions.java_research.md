# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestPathExceptions.java

Purpose: Tests Hadoop `PathIOException` message formatting, path retention, wrapping of causes, custom messages, and remote exception reconstruction.

Important APIs/types/functions: `PathIOException`, `Path`, `RemoteException.unwrapRemoteException`, JUnit assertions. Fields `path = "some/file"` and `error = "KABOOM"` define the common fixture.

Control flow: Each test constructs a `PathIOException` through a different constructor and compares `getPath()` and `getMessage()` against exact expected strings. The remote test constructs `RemoteException` objects naming `PathIOException` and verifies both generic and typed unwrap paths produce `PathIOException` instances.

State/persistence: No persistent state; all exception objects are in-memory.

Dependencies/integration: Integrates filesystem path exception semantics with Hadoop IPC `RemoteException` deserialization/unwrap behavior, which is important for clients receiving server-side filesystem errors.

Risks: Message tests are intentionally brittle; wording changes in `PathIOException` will fail these tests even when behavior is otherwise compatible. The local `pe` assignments in the remote test are unused except as constructor coverage hints.

Test signals: Exact path object equality, exact message strings, and `instanceof PathIOException` after remote unwrap.
