<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestServletFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestServletFilter.java

## Purpose
Tests servlet filter registration and initialization failure behavior in `HttpServer2`. It verifies global filter initialization via configuration, context-specific registration through `HttpServer2.defineFilter`, and wrapping of filter init exceptions into server startup failures.

## Important APIs, Types, and Functions
`SimpleFilter` implements `javax.servlet.Filter`, records the request URI in static volatile `uri`, and forwards to the filter chain. `SimpleFilter.Initializer` extends `FilterInitializer` and adds the filter to a `FilterContainer`. `ErrorFilter` extends `SimpleFilter` but throws `ServletException` from `init`. `access()` opens a URL and drains its input stream while tolerating normal HTTP IO exceptions. Tests use `HttpServerFunctionalTest.createTestServer`, `HttpServer2.FILTER_INITIALIZER_PROPERTY`, `NetUtils.getHostPortString`, and `GenericTestUtils.assertExceptionContains`.

## Control Flow and State
The unannotated `testServletFilter()` starts a server with `SimpleFilter`, generates a random access sequence over `/fsck`, `/stacks`, `/a.jsp`, `/logs/a.log`, and `/static/hadoop-logo.jpg`, and checks that `/fsck` bypasses filtering while the other paths update `uri`. Annotated tests start servers with `ErrorFilter` through the initializer and context API and assert startup failures. The only mutable state is static `uri`, reset after each filtered request.

## Dependencies and Integration Points
Depends on servlet API, Hadoop HTTP filter initializer/container contracts, URLConnection, and the test HTTP server harness. The path filtering behavior reflects `HttpServer2`'s default exclusion of certain internal endpoints such as `/fsck`.

## Risks and Test Signals
The static `uri` can be sensitive to concurrent test execution, and `testServletFilter()` lacks `@Test` in this source, so runner behavior may omit it. Strong signals are correct exception wrapping (`Problem starting http server`, `Unable to initialize WebAppContext`) and filter URI capture for non-excluded paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestServletFilter.java -->
