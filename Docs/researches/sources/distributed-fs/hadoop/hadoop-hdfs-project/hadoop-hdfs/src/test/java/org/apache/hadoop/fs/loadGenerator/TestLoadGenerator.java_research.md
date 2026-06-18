<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/loadGenerator/TestLoadGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/loadGenerator/TestLoadGenerator.java

Purpose: Tests HDFS load-generator support utilities: structure generation, data generation, probabilistic load generation, argument validation, and scripted operations.
Important APIs/types/functions: `TestLoadGenerator` extends `Configured` and implements `Tool`; tests `StructureGenerator`, `DataGenerator`, `LoadGenerator`, `main()`, and `run()`.
Control flow: Static configuration sets tiny block/checksum sizes and heartbeat interval. `testStructureGenerator()` runs with deterministic args/seed, verifies generated directory/file structure files, then mutates arguments to assert validation failures. `testLoadGenerator()` writes structure files, starts a three-Datanode cluster, generates data under `/test`, runs load generation, validates bad probabilities/delays/thread/time args, and tests good/bad script files.
State and persistence behavior: State includes files under `PathUtils.getTestDir`, generated HDFS namespace under `/test`, and temporary script files. Cleanup deletes structure/script files and shuts down the cluster.
Dependencies and integration points: Integrates `StructureGenerator`, `DataGenerator`, `LoadGenerator`, MiniDFSCluster, `ToolRunner`, and Hadoop `Time`.
Risks and edge cases: Generated output is seed-sensitive. Argument index constants must match the argv arrays; one restore line assigns `args[READ_PROBABILITY] = oldArg` after mutating write probability, which is suspicious but in-test. Long-running load operations depend on timing.
Test signals: Signals include exact generated file lines, zero return for valid generation/load/script runs, -1 for invalid args and malformed scripts, and successful `Tool` wrapper execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/loadGenerator/TestLoadGenerator.java -->
