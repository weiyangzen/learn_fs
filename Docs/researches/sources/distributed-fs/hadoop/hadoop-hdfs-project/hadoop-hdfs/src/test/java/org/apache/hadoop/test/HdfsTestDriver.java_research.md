# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/test/HdfsTestDriver.java

## Purpose
`HdfsTestDriver` is a command-line program driver for HDFS test utilities that should not depend on MapReduce APIs.

## Important APIs, types, and functions
- Constructor registers `dfsthroughput` mapped to `BenchmarkThroughput` and `minidfscluster` mapped to `MiniDFSClusterManager` in a `ProgramDriver`.
- `run(String[])` delegates to `ProgramDriver.run` and exits the JVM with the returned code.
- `main` constructs the driver and runs it.

## Control flow
Construction registers commands inside a broad `Throwable` catch. `run` initializes exit code to `-1`, tries to run the selected command, catches broad `Throwable`, prints stack traces, and calls `System.exit(exitCode)`.

## State and persistence behavior
The only state is the `ProgramDriver` instance and its command registry. Running commands may start clusters or benchmarks, but this file itself persists no data.

## Dependencies and integration points
It integrates Hadoop `ProgramDriver`, HDFS `BenchmarkThroughput`, and `MiniDFSClusterManager`. It is likely invoked from test jars or command-line HDFS test tooling.

## Risks and edge cases
Broad exception handling prints stack traces rather than structured logs. `System.exit` makes direct unit testing harder unless `ExitUtil` or process isolation is used. Registration failure leaves the driver partially populated.

## Test signals
No local tests are defined here. Functional signals come from invoking registered subcommands and verifying expected exit codes and behavior.
