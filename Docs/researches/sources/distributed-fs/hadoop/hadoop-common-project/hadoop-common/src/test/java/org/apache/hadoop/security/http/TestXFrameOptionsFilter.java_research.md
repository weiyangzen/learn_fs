<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestXFrameOptionsFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestXFrameOptionsFilter.java

## Purpose
Tests `XFrameOptionsFilter` default and configured `X-Frame-Options` behavior, including whether downstream filters see the header and whether downstream code can override it.

## Important APIs, Types, And Functions
The tests instantiate `XFrameOptionsFilter`, configure `XFrameOptionsFilter.CUSTOM_HEADER_PARAM`, and observe `HttpServletResponse.setHeader`, `containsHeader`, and the wrapper type `XFrameOptionsFilter.XFrameOptionsResponseWrapper`.

## Control Flow
`testDefaultOptionsValue` initializes with no custom value, expects `DENY`, and asserts the header is visible inside the filter chain. `testCustomOptionsValueAndNoOverrides` initializes with `SAMEORIGIN`, has the chain try to set `X-Frame-Options` to another value, and verifies only the configured value reaches the underlying response.

## State And Persistence
Only per-filter configuration and the response wrapper's header state are involved. The test accumulates observed header values in an in-memory collection.

## Dependencies And Integration Points
Uses servlet mocks, Mockito `Answer`, AssertJ, and JUnit assertions. It validates the security response-header contract used by Hadoop HTTP endpoints.

## Risks
The tests cover `setHeader` but not all possible header mutation APIs such as `addHeader` unless the production wrapper maps them internally. They also do not exercise multiple filter invocations on the same response object.

## Test Signals
Successful signals are one observed `X-Frame-Options` value, value `DENY` by default, value `SAMEORIGIN` under custom config, wrapper visibility inside the chain, and no downstream override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestXFrameOptionsFilter.java -->
