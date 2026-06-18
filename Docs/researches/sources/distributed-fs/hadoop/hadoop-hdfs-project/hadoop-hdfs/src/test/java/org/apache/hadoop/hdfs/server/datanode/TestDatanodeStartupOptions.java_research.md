# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeStartupOptions.java

Purpose: verifies DataNode command-line startup option parsing and storage of the parsed `StartupOption` in configuration.

Important APIs and types: `DataNode.parseArguments`, `DataNode.getStartupOption`, `HdfsConfiguration`, and `HdfsServerConstants.StartupOption`. AssertJ is used for boolean and enum equality.

Control flow: `initConfiguration` creates a fresh config before each test because parsing mutates configuration. `checkExpected` copies varargs into a String array, calls `DataNode.parseArguments`, obtains `DataNode.getStartupOption`, and checks parse success plus expected option when success is expected. `testStartupSuccess` covers no args, `-regular`, uppercase `-REGULAR`, and `-rollback`. `testStartupFailure` covers an unknown option and a single combined string `"-regular -rollback"` that should not parse as two valid options.

State and persistence behavior: only the in-memory configuration is mutated. Integration point is DataNode CLI parsing used before DN startup. Risks are limited: the failure case with a combined string tests one shell-tokenization shape, not all conflicting option arrays. Test signals are parse return values and `StartupOption` enum stored in config.
