# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/JmxServlet.java

## Purpose
`JmxServlet` exposes read-only JMX data as JSON over HTTP, with optional query parameters for whole-bean or single-attribute lookup.

## Important APIs, Types, and Functions
Important methods are `init()`, `doTrace()`, `doGet()`, `listBeans()`, `writeAttribute(ObjectName, MBeanAttributeInfo)`, `writeAttribute(String, Object)`, and `writeObject()`. It uses platform `MBeanServer`, Jackson `JsonFactory`/`JsonGenerator`, JMX metadata and open-mbean types, and servlet response status codes.

## Control Flow, State, and Persistence
`init()` stores the platform MBean server and JSON factory. `doTrace()` returns method-not-allowed. `doGet()` sets JSON content type and permissive access-control headers, then handles `get=objectName:::attribute` for one attribute or `qry=pattern` for a bean query, defaulting to `*:*`. `listBeans()` queries names, gets bean info, handles modelerType specially, optionally fetches a single attribute, or iterates readable attributes while filtering invalid field names. `writeObject()` recursively emits arrays, numbers, booleans, composite data, tabular data, strings, and nulls.

## Dependencies and Integration Points
It is mounted by `WebServer` at `/metrics/jmx`. It integrates with JVM/platform MBeans and any Alluxio metrics exposed through JMX.

## Risks and Test Signals
Risks include broad unauthenticated JMX exposure at this layer, wildcard queries that can be expensive, recursive data serialization complexity, partial output when a single attribute is missing, and many caught reflection/runtime errors being logged and skipped. Signals are `/metrics/jmx?qry=...` JSON output, `/metrics/jmx?get=...` success and 404 behavior, TRACE rejection, malformed object name returning 400, and serialization of composite/tabular data.
