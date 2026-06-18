<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorStream.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorStream.java

Purpose: Regression test for `CompressorStream.close()` ensuring the stream marks itself closed even when `finish()` throws an `IOException`.

Important APIs/types/functions: the test class itself extends `CompressorStream`, creates static file/output stream resources for `tmp.txt`, overrides `finish()` to throw, and tests `close()`.

Control flow: static initializer creates `tmp.txt` and a `FileOutputStream`. Constructor calls `super(fop)`. `testClose` creates the subclass, calls `close`, catches the expected IOException, then asserts the inherited `closed` flag is true and deletes the file.

State and persistence behavior: creates a file named `tmp.txt` in the working directory and deletes it at test end. Static stream/file state is shared for the class lifetime.

Dependencies and integration points: directly exercises protected/internal state of `CompressorStream` via subclassing in the same package.

Risks and edge cases: static file output stream may remain open; deletion can be platform-sensitive. Fixed file name is unsafe under parallel execution. The test only checks `closed` flag, not whether the underlying `FileOutputStream` is closed.

Test signals: verifies `close()` handles exceptional `finish()` by still transitioning to closed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorStream.java -->
