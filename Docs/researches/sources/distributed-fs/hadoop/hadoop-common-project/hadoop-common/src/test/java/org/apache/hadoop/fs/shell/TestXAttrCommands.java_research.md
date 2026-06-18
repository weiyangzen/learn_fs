# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestXAttrCommands.java

Purpose: Validates command-line argument checks for FS shell extended attribute commands `-getfattr` and `-setfattr`.

Important APIs/types/functions: `FsShell`, `ToolRunner.run`, `Configuration`, `System.err` redirection to `ByteArrayOutputStream`, helper `runCommand`.

Control flow: `setup` captures and replaces `System.err`, resets an error buffer, and creates a fresh configuration. `testGetfattrValidations` runs invalid command combinations: missing path with `-d`, extra argument, missing `-n`/`-d`, and unsupported encoding. `testSetfattrValidations` covers missing path, extra arguments, and missing `-n`/`-x`. Each case expects a nonzero return and an error substring. `cleanUp` restores stderr.

State/persistence: Temporarily mutates JVM-global `System.err`, which is restored after each test. No filesystem xattrs are read or written.

Dependencies/integration: Exercises full `FsShell` command dispatch and option validation through `ToolRunner`, not just parser internals.

Risks: Global stderr replacement can interfere with concurrently running tests if not isolated. Assertions use substring matching for diagnostics and do not validate exact usage text. No positive xattr operations are covered.

Test signals: Nonzero command exit status and expected diagnostic fragments for invalid argument combinations.
