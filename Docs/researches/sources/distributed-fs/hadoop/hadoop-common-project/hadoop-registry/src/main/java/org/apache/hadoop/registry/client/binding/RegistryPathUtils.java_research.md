<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryPathUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryPathUtils.java

## Purpose

Static helpers for validating, joining, splitting, encoding, and inspecting registry paths. The source was read as a complete 237-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryPathUtils`, `public static String validateZKPath(String path) throws`, `public static String validateElementsAsDNS(String path) throws`, `public static String createFullPath(String base, String path) throws`, `public static String join(String base, String path)`, `public static List<String> split(String path)`, `public static String lastPathEntry(String path)`, `public static String parentOf(String path) throws PathNotFoundException`, `public static String encodeForRegistry(String element)`, `public static String encodeYarnID(String yarnId)`.

## Control Flow

validateZKPath delegates to ZooKeeper PathUtils; validateElementsAsDNS checks each element with IDN conversion and DNS label regex; join normalizes slashes; parentOf rejects root/no-parent cases.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `Preconditions`, `InterfaceAudience`, `InterfaceStability`, `PathNotFoundException`, `InvalidPathnameException`, `RegistryInternalConstants`, `PathUtils`, `IDN`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Path conversion uses punycode and regex constraints; edge cases include root paths, trailing slashes, and non-ASCII usernames.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryPathUtils.java -->
