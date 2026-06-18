<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/build-and-install.sh -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/build-and-install.sh

## Purpose

Builds the Hadoop 2 OrangeFS adapter jar with Maven using Java 7 source/target settings, skips tests, and installs the versioned jar into `ORANGEFS_PREFIX/lib`.

## Important APIs, Types, and Functions

This is an operational shell entry point rather than a library API. Its interface is the script name, positional arguments where documented, and required environment variables from comments or sourced `setenv` files.

Observed command surface:

- `cd $(dirname $0)`
- `sudo cp target/orangefs-hadoop2-?.?.?.jar "${ORANGEFS_PREFIX}/lib/"`

## Control Flow

The script changes to its own directory, runs `mvn ... clean package`, and only copies the jar if Maven succeeds because the commands are chained with `&&`.

## State, Persistence, and Concurrency

The script changes daemon state, local temporary state, benchmark data, logs, or OrangeFS example storage depending on its role. It performs no locking, so concurrent invocations can race with daemons, SSH cleanup, benchmark runs, or jar updates.

## Dependencies and Integration Points

Requires Maven, a compatible JDK, generated `pom.xml`, `ORANGEFS_PREFIX`, sudo rights, and the OrangeFS JNI artifact available to Maven.

## Risks and Test Signals

Skipping tests can install a broken adapter. The wildcard jar copy assumes exactly one matching target jar. Test by running Maven with tests separately and verifying Hadoop can load `org.apache.hadoop.fs.ofs.OrangeFileSystem`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/build-and-install.sh -->
