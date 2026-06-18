<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/JsonSerDeser.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/JsonSerDeser.java

## Purpose

JSON byte marshaller/unmarshaller for registry records. The source was read as a complete 117-line file for this research item.

## Important APIs, Types, and Functions

Important APIs/types/functions: `public class JsonSerDeser<T> extends JsonSerialization<T>`, `public JsonSerDeser(Class<T> classType)`, `public T fromBytes(String path, byte[] bytes) throws IOException`, `public T fromBytes(String path, byte[] bytes, String marker)`.

## Control Flow

Extends JsonSerialization<T>; fromBytes rejects null/empty payloads with NoRecordException, decodes UTF-8, parses JSON, and wraps JsonProcessingException as InvalidRecordException.

## State and Persistence Behavior

State behavior depends on file role: API/constants/package files hold no runtime state; factories mutate or initialize services; filesystem registry stores records as JSON bytes in `_record` files; CLI owns a service lifecycle until close.

## Dependencies and Integration Points

Direct dependencies include `JsonProcessingException`, `StringUtils`, `InterfaceAudience`, `InterfaceStability`, `InvalidRecordException`, `NoRecordException`, `JsonSerialization`, `EOFException`, and others. Integration points include Hadoop Service lifecycle, RegistryOperations, ServiceRecord/Endpoint types, ZooKeeper/Curator or FileSystem backends, and CLI/configuration consumers as applicable.

## Risks and Edge Cases

String marker parameter is unused beyond signature; invalid charset is not expected because StandardCharsets.UTF_8 is fixed.

## Test Signals

Test signals include registry unit/integration tests for path validation, service record JSON round-trips, auth factory configuration, filesystem backend CRUD, CLI argument parsing, SpotBugs/RAT, and Maven Surefire module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/main/java/org/apache/hadoop/registry/client/binding/JsonSerDeser.java -->
