# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractContentSummaryTest.java

Purpose: `AbstractContractContentSummaryTest` checks `FileSystem.getContentSummary(Path)` behavior for a nested directory tree and for missing paths.

Important APIs and types: it uses `ContentSummary`, `FileSystem`, `Path`, AssertJ assertions, `ContractTestUtils.touch`, and `LambdaTestUtils.intercept`. It extends `AbstractFSContractTestBase` for filesystem selection and path construction.

Control flow: `testGetContentSummary()` creates `parent`, a nested `a/b/c` path, and a touched file below that nested path. It calls `fs.getContentSummary(parent)` and expects four directories and one file. `testGetContentSummaryIncorrectPath()` creates only `parent`, then requests a summary of missing `parent/a` and expects `FileNotFoundException`.

State and persistence behavior: the test builds a small persisted namespace under the contract test path. It verifies that summary traversal counts all directories under the queried parent, including the parent itself and nested descendants, while reporting exactly one file.

Dependencies and integration points: it depends on `mkdirs()` and `touch()` semantics being functional. It does not feature-gate content summaries, so concrete contract suites including this test are expected to provide an implementation of `getContentSummary`.

Risks: the nested file path is constructed through string concatenation (`path(nested + "file.txt")`), which depends on `Path.toString()` formatting and may produce a file name appended to the nested path string without an explicit separator. The expected directory count is tightly coupled to Hadoop `ContentSummary` semantics, including the queried directory.

Test signals: pass indicates content summary correctly recurses into nested directories, counts files and directories, and rejects nonexistent paths with `FileNotFoundException`.
