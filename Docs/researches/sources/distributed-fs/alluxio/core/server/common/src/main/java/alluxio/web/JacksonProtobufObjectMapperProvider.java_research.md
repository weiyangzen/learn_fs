# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/JacksonProtobufObjectMapperProvider.java

## Purpose
`JacksonProtobufObjectMapperProvider` supplies Jersey with a Jackson `ObjectMapper` configured for protobuf JSON conversion.

## Important APIs, Types, and Functions
It implements `ContextResolver<ObjectMapper>`, constructs `mDefaultObjectMapper`, defines `createDefaultMapper()`, and returns the mapper from `getContext(Class<?>)`. The mapper uses lower-camel-case property naming and registers HubSpot's `ProtobufModule`.

## Control Flow, State, and Persistence
Construction creates one mapper instance. Every context lookup returns the same mapper independent of type. There is no persistence.

## Dependencies and Integration Points
It depends on Jackson, Jersey `@Provider`, and `ProtobufModule`. REST endpoints use it when converting protobuf-backed request/response types.

## Risks and Test Signals
Risks include global mapper mutation by consumers, protobuf module compatibility, and lower-camel-case assumptions. Signals are REST JSON/protobuf serialization and deserialization tests for representative proto messages.
