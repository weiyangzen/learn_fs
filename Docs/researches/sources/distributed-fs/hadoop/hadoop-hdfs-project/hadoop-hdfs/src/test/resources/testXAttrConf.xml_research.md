# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/resources/testXAttrConf.xml

Purpose: XML testConf input for HDFS extended attribute CLI behavior. It drives shell-command style tests for `-setfattr` and `-getfattr` against `NAMENODE`, covering namespace validation, value encodings, removal, recursion, raw namespace access through `/.reserved/raw`, and the special `security.hdfs.unreadable.by.superuser` attribute.

Important structure and APIs: the file contains `<configuration><mode>test</mode><tests>...` with repeated `<test>` entries. Each entry has a description, ordered `<test-commands>`, cleanup commands, and comparators. Comparator types include `SubstringComparator` for diagnostic fragments and `ExactComparator` for fully normalized output strings using `#LF#`.

Control flow: the test harness executes commands in declaration order, then cleanup commands, then compares command output with expected comparator output. Tests create `/file1` or `/dir1`, mutate xattrs, invoke read/list commands, and validate positive and negative behavior. Error-path tests intentionally verify permission failures, invalid namespace prefixes, invalid encoding names, missing attributes, undeletable security xattrs, and access denial when a protected file is fetched.

State and persistence behavior: state is entirely HDFS namespace metadata created during each test. Cleanup removes created files or directories and one local `/tmp/file1` artifact. The raw namespace tests depend on the same underlying `/file1` object while addressing it through `/.reserved/raw/file1`.

Dependencies and integration points: consumed by Hadoop's `testConf.xml` XML-driven CLI test framework and HDFS command implementations for `setfattr`/`getfattr`. It relies on HDFS xattr namespace semantics: `user`, `trusted`, `security`, `system`, and `raw`; superuser/security restrictions; encoding handling for text, hex, and base64; recursive `getfattr -R`; and reserved raw-path behavior.

Risks: expectations are brittle around exact CLI error text, output ordering, and newline normalization. Tests touching `/tmp/file1` assume local cleanup is safe and that the process has local filesystem permissions. Namespace permissions can vary if the harness user or cluster security mode changes.

Test signals: successful execution demonstrates xattr round trips, prefix validation, permission rejection for protected namespaces, immutable unreadable-by-superuser behavior, raw namespace isolation, encoding conversion, xattr deletion, missing-attribute diagnostics, and recursive listing output.
