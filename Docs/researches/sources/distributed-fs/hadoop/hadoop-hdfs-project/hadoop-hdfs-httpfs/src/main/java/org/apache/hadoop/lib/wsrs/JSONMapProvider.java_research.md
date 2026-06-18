# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/JSONMapProvider.java

## Purpose
`JSONMapProvider` is a Jersey `MessageBodyWriter` that serializes Java `Map` responses as UTF-8 JSON.

## Important APIs, Types, and Functions
It is annotated with `@Provider` and `@Produces(MediaType.APPLICATION_JSON + "; " + JettyUtils.UTF_8)`. `isWriteable` accepts classes assignable to `Map`. `getSize` returns `-1`. `writeTo` serializes with `JSONObject.toJSONString(map)`, appends the platform newline, and writes UTF-8 bytes.

## Control Flow
During response writing, Jersey selects the provider for map entities, serializes the complete map into a string, and writes it to the output stream.

## State and Persistence
The provider is stateless. It has no persistence; its side effect is writing HTTP response bytes.

## Dependencies and Integration Points
It depends on Jersey, `org.json.simple.JSONObject`, Hadoop `JettyUtils.UTF_8`, and HttpFS resource methods that return `Map` objects for JSON APIs.

## Risks
The provider materializes the entire JSON string before writing, which is fine for small metadata maps but not for large responses. Raw `Map` typing means generic type validation is absent. Platform-specific newline is appended to every JSON response.

## Test Signals
`BaseTestHttpFSWith` compares JSON-derived filesystem metadata for block locations, snapshots, server defaults, quotas, and erasure coding; those flows depend on consistent JSON response serialization.
