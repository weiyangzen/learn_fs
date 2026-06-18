# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/find/TestPrint0.java

Purpose: Tests the `-print0` find action variant.

Important APIs/types/functions: `Print.Print0`, `FindOptions.setOut`, `PathData`, `PrintStream.print`, `Result.PASS`.

Control flow: A fresh `Print.Print0` gets a mocked `PrintStream` through `FindOptions`; applying it to `/one/two/test` returns `PASS` and writes the path followed by NUL (`'\0'`).

State/persistence: No external state. Uses mock filesystem only for `PathData` construction.

Dependencies/integration: Ensures the NUL-delimited action uses `FindOptions` output and shares the same `PathData` string representation as `Print`.

Risks: Covers only a simple path and does not validate consumers or binary-safe stream behavior beyond exact delimiter.

Test signals: Exact `out.print(filename + '\0')` and no extra output interactions.
