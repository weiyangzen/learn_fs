# sources/distributed-fs/orangefs/src/client/jni/src/test/java/org/orangefs/usrint/OrangeFileSystemLayoutTest.java
## sources/distributed-fs/orangefs/src/client/jni/src/test/java/org/orangefs/usrint/OrangeFileSystemLayoutTest.java

**Purpose:** JUnit test coverage for the `OrangeFileSystemLayout` enum's numeric values and standard enum lookup names.

**APIs and control flow:** `testGetLayout()` asserts each enum constant returns the expected integer 1 through 5. `testLayoutUsingValueOf()` asserts `valueOf(String)` returns each named constant.

**State and dependencies:** Depends only on JUnit 4 assertions and the enum class. It does not need OrangeFS native libraries or an OrangeFS mount.

**Risks and tests:** This is a useful ABI guard for Java-side constants but only detects source-level enum drift. It does not prove that native C layout constants match, that `openWithHints` accepts the values, or that layout behavior is honored by the filesystem. Integration tests should complement it by creating files with each layout and checking native results.
