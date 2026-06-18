# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSJSONReader.java

## Purpose
`KMSJSONReader.java` is a Jersey JSON request body reader for KMS endpoints that accept untyped `Map` or `List` payloads.

## Important APIs, Types, and Functions
It implements `MessageBodyReader<Object>`, is annotated with `@Provider` and `@Consumes(MediaType.APPLICATION_JSON)`, and uses a static Jackson `ObjectMapper`. `isReadable` allows payload binding when the requested type is assignable from `Map` or `List`. `readFrom` deserializes the entity stream into the requested class.

## Control Flow
Jersey invokes this provider for JSON requests targeting raw `Map` or `List` endpoint parameters such as key creation material and reencryption batches. Deserialization errors propagate as `IOException` or `WebApplicationException` and are later mapped by the exception provider.

## State and Persistence
The only state is the shared mapper. It writes no persistent state.

## Dependencies and Integration Points
It integrates with Jersey provider discovery and the raw JSON payloads consumed by `KMS.java`. It depends on Jackson databind.

## Risks
The reader targets raw collections, so type validation is deferred to endpoint code and utility parsers. Numeric values are deserialized according to Jackson defaults, which matters for fields cast to `Integer` in `KMS.createKey`.

## Test Signals
Tests should verify Map/List binding, invalid JSON propagation, numeric field type behavior, and that unrelated types are not claimed by this provider.
