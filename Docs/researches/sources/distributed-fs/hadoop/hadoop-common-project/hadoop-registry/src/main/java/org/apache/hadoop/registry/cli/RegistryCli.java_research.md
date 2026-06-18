<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/cli/RegistryCli.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/cli/RegistryCli.java

## Purpose

Command-line Tool for registry ls, resolve, bind, mknode, and rm operations. The source was read as a complete 496-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryCli extends Configured implements Tool, Closeable`, `public RegistryCli(PrintStream sysout, PrintStream syserr)`, `public RegistryCli(RegistryOperations reg,`, `public static void main(String[] args) throws Exception`, `public void close() throws IOException`, `public int run(String[] args) throws Exception`, `public int ls(String[] args)`, `public int resolve(String[] args)`, `public int bind(String[] args)`, `public int mknode(String[] args)`.

## Control Flow

Constructs/starts RegistryOperations, parses commons-cli options, builds ServiceRecord endpoints, validates absolute paths, invokes registry operations, and maps exceptions to user messages.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `*`, `Closeable`, `IOException`, `PrintStream`, `URI`, `URISyntaxException`, `List`, `Map`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Uses deprecated GnuParser; bind always overwrites; main terminates via ExitUtil; option parsing relies on exact arg positions.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/cli/RegistryCli.java -->
