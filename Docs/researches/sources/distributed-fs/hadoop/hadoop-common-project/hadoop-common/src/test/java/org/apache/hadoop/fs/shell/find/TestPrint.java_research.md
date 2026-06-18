# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/find/TestPrint.java

Purpose: Tests the default `-print` find action.

Important APIs/types/functions: `Print`, `FindOptions.setOut`, `PathData`, `PrintStream.print`, `Result.PASS`.

Control flow: The test resets the mock filesystem, creates a `Print` action with a mocked output stream, applies it to `/one/two/test`, expects `Result.PASS`, and verifies stdout receives the filename followed by newline.

State/persistence: No persistent state; output is a Mockito mock.

Dependencies/integration: Confirms `Print` uses `PathData.toString()` and the `FindOptions` output stream rather than global stdout.

Risks: Only one path and delimiter are tested; no coverage of null streams or unusual printable string behavior.

Test signals: Exact call `out.print(filename + '\n')` and no other output interactions.
