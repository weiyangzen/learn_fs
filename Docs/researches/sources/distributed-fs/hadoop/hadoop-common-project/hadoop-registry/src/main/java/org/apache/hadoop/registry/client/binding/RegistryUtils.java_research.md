<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryUtils.java

## Purpose

Higher-level registry path/user and record extraction utilities. The source was read as a complete 398-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryUtils`, `public static String homePathForUser(String username)`, `public static String convertUsername(String username)`, `public static String serviceclassPath(String user,`, `public static String servicePath(String user,`, `public static String componentListPath(String user,`, `public static String componentPath(String user,`, `public static Map<String, ServiceRecord> listServiceRecords(`, `public static Map<String, RegistryPathStatus> statChildren(`, `public static String homePathForCurrentUser()`.

## Control Flow

Builds user/service/component paths, converts Kerberos/user names, honors HADOOP_USER_NAME in insecure mode, stats child paths, resolves service records, and skips EOF/invalid/no-record children.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `VisibleForTesting`, `Preconditions`, `StringUtils`, `InterfaceAudience`, `InterfaceStability`, `PathNotFoundException`, `UserGroupInformation`, `RegistryConstants`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

List/extract operations are non-atomic and tolerate deleted/invalid children; username conversion affects DNS-safe service discovery names.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryUtils.java -->
