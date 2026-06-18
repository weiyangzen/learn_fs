# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestHardLink.java

Purpose: tests Hadoop `HardLink` helpers against the host local filesystem: link count discovery, single hardlink creation, multi-file hardlink creation, empty batches, and Windows command-template syntax.

Important APIs/types/functions: static imports from `HardLink` including `createHardLink`, `createHardLinkMult`, `getLinkCount`, `supportsHardLink`, and `HardLinkCGWin`. Helpers build source/target directories and validate content/link counts.

Control flow/state/persistence: `@BeforeAll` and `@AfterEach` delete static temp directories; `@BeforeEach` recreates `src`, `tgt_one`, and `tgt_mult` with three files containing unique strings. Single-link tests create multiple links to the same source and then append through one link to prove shared inode content. Multi-link tests hardlink all names from a directory and verify count/content. Empty-list test ensures no filesystem change. Windows syntax test inspects command array literals without executing Windows commands.

Dependencies/integration points: depends on local filesystem hardlink support, Hadoop `FileUtil`, Java `FileReader/FileWriter`, and OS-specific command generation.

Risks/test signals: tests are intentionally lightweight and assume permissions are valid; they do not cover negative permission failures. They catch link count regressions, content-copy masquerading as hardlinking, empty-batch side effects, and accidental command string mangling on Windows.
