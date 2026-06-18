# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/jmx/TestJMXJsonServlet.java

## Purpose

`TestJMXJsonServlet` validates Hadoop's `/jmx` servlet JSON output, query/get parameters, NaN rendering when filtering is disabled, CORS headers, and disallowed HTTP TRACE handling.

## Important APIs, Types, And Functions

The test extends `HttpServerFunctionalTest`, uses `createTestServer()`, `getServerURL()`, `readOutput(URL)`, `JMXJsonServlet.ACCESS_CONTROL_ALLOW_METHODS`, `ACCESS_CONTROL_ALLOW_ORIGIN`, and regex helper `assertReFind()`.

## Control Flow

`@BeforeAll` starts a test `HttpServer2`. `testQuery()` fetches `/jmx?qry=java.lang:type=Runtime`, `/jmx?qry=java.lang:type=Memory`, full `/jmx` output after setting a system property to `Float.NaN`, and `/jmx?get=java.lang:type=Memory::HeapMemoryUsage`. It also checks an invalid get request returns `"ERROR"` and confirms CORS headers. `testTraceRequest()` sends TRACE and expects HTTP 405.

## State And Persistence Behavior

The server runs in-memory on an ephemeral port. The test mutates a JVM system property to expose NaN behavior. No durable state is written.

## Dependencies And Integration Points

This tests `HttpServer2`, the JMX servlet, Java platform MBeans, servlet response codes, and HTTP URL connection behavior. It is an integration surface for Hadoop web UIs exposing JMX JSON.

## Risks And Test Signals

Risks include brittle regexes against JSON formatting, global system-property leakage, servlet method security regressions, and CORS header changes. Signals are regex matches for bean names/modeler type/NaN, invalid get error output, CORS header presence, and 405 for TRACE.
