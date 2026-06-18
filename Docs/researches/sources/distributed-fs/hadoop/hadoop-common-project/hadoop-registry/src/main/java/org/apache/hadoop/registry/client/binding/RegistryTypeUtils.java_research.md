<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryTypeUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryTypeUtils.java

## Purpose

Static helpers for building and validating ServiceRecord Endpoint objects. The source was read as a complete 291-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class RegistryTypeUtils`, `public static Endpoint urlEndpoint(String api,`, `public static Endpoint restEndpoint(String api,`, `public static Endpoint webEndpoint(String api,`, `public static Endpoint inetAddrEndpoint(String api,`, `public static Endpoint ipcEndpoint(String api, InetSocketAddress address)`, `public static Map<String, String> map(String key, String val)`, `public static Map<String, String> uri(String uri)`, `public static Map<String, String> hostnamePortPair(String hostname, int port)`, `public static Map<String, String> hostnamePortPair(InetSocketAddress address)`.

## Control Flow

Creates URL/REST/web/inet/ipc endpoints, address maps, URI lists, URL conversions, and validates ServiceRecord/Endpoint instances.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `Preconditions`, `InterfaceAudience`, `InterfaceStability`, `InvalidRecordException`, `Endpoint`, `ProtocolTypes`, `ServiceRecord`, `InetSocketAddress`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

Validation catches endpoint shape but not service reachability; malformed URI/URL values surface when retrieval helpers parse them.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/RegistryTypeUtils.java -->
