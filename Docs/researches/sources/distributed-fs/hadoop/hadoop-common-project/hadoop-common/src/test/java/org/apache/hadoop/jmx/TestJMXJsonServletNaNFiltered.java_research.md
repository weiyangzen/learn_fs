# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/jmx/TestJMXJsonServletNaNFiltered.java

## Purpose

`TestJMXJsonServletNaNFiltered` verifies the `/jmx` servlet replaces NaN values with numeric `0.0` when `JMX_NAN_FILTER` is enabled.

## Important APIs, Types, And Functions

The test uses `Configuration.setBoolean(JMX_NAN_FILTER, true)`, `HttpServerFunctionalTest.createTestServer(configuration)`, `readOutput()`, and regex helper `assertReFind()`.

## Control Flow

The server is started once with NaN filtering enabled. The test sets the system property `THE_TEST_OF_THE_NAN_VALUES` to `Float.NaN`, reads `/jmx`, and asserts the property entry appears with `value` equal to `0.0` rather than the string `"NaN"`.

## State And Persistence Behavior

State is limited to the test HTTP server and JVM system property. There is no persisted state, but the system-property mutation is global to the JVM.

## Dependencies And Integration Points

It integrates Hadoop configuration, `HttpServer2`, `JMXJsonServlet`, and platform MBean system-property exposure. It complements the unfiltered servlet test.

## Risks And Test Signals

Risks include mismatched numeric/string rendering, global property leakage, and JSON formatting sensitivity. The signal is a full servlet request proving filtered NaN values become `0.0` in emitted JSON.
