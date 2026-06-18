# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/wsrs/JSONProvider.java

## Purpose
`JSONProvider` is a Jersey `MessageBodyWriter` for `JSONStreamAware` response entities.

## Important APIs, Types, and Functions
It is annotated with `@Provider` and JSON UTF-8 `@Produces`. `isWriteable` accepts classes assignable to `JSONStreamAware`. `writeTo` wraps the output in an `OutputStreamWriter` using UTF-8, calls `writeJSONString`, appends a newline, and flushes.

## Control Flow
Jersey invokes this provider for JSON-simple streaming objects. The provider writes through the entity's own JSON streaming method, then flushes but does not close the servlet output stream.

## State and Persistence
The provider is stateless and only writes response bytes.

## Dependencies and Integration Points
It depends on `org.json.simple.JSONStreamAware`, Jersey, and Hadoop Jetty UTF-8 constants. HttpFS resources can return JSON-simple objects directly and rely on provider package scanning in `web.xml`.

## Risks
The provider flushes the writer, which is usually safe but can affect response buffering. Like `JSONMapProvider`, it appends a platform newline. Any exception during `writeJSONString` becomes a response write failure.

## Test Signals
Metadata-heavy operations in `BaseTestHttpFSWith`, including snapshot and erasure-coding comparisons, provide high-level coverage for JSON response compatibility.
