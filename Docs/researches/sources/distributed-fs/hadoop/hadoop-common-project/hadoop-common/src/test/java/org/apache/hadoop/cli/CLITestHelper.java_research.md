# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/cli/CLITestHelper.java

Purpose: reusable JUnit CLI test harness that reads XML test definitions, expands placeholders, executes commands, applies comparators, records results, and logs a detailed pass/fail summary.

Important APIs/classes: constants `TESTMODE_TEST`, `TESTMODE_NOCOMPARE`, `TEST_CACHE_DATA_DIR`; lifecycle `setUp`, `tearDown`; parser factory `getConfigParser`; command expansion `expandCommand`; runner `testAll`; abstract `execute`; inner SAX `TestConfigFileParser`.

Control flow: setup parses `testConf.xml` from the test cache and creates a security-enabled `Configuration`. `testAll` iterates parsed tests, executes all test commands, applies dynamic comparator classes by name, checks optional expected exit code, stores actual output/result data, then runs cleanup commands. Tear down logs details and asserts global success.

State and persistence: keeps parsed tests, comparator data, Hadoop configuration, data-dir URI, username placeholder, and mutable test mode in instance fields. It redirects no global streams itself, but `CommandExecutor` does during execution.

Dependencies/integration: uses secure SAX parsing through `XMLUtils`, JUnit 5 assertions, `Shell.WINDOWS` filtering, `FsShell` command types through utility classes, and comparator classes in `org.apache.hadoop.cli.util`.

Risks and test signals: comparator class loading via string is fragile; `username` is never initialized here while expansion replaces `USERNAME`; only the last command result in a multi-command test is compared; XML character accumulation preserves whitespace. Tests should validate parser behavior, Windows-only filtering, nocompare mode, cleanup execution after failures, and exact summary assertions.
