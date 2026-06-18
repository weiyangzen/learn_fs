<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestRestCsrfPreventionFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestRestCsrfPreventionFilter.java

## Purpose
Tests `RestCsrfPreventionFilter` decisions for browser-like requests, non-browser user agents, required CSRF headers, custom header names, and ignored HTTP methods. It is a focused servlet-filter unit test using Mockito mocks rather than a servlet container.

## Important APIs, Types, And Functions
The class exercises `RestCsrfPreventionFilter.init()` and `doFilter()` with mocked `FilterConfig`, `HttpServletRequest`, `HttpServletResponse`, and `FilterChain`. Constants under test include `CUSTOM_HEADER_PARAM`, `CUSTOM_METHODS_TO_IGNORE_PARAM`, `BROWSER_USER_AGENT_PARAM`, `HEADER_DEFAULT`, and `HEADER_USER_AGENT`.

## Control Flow
Each test builds filter init parameters, stubs request headers and methods, initializes a new filter, then calls `doFilter`. Good requests must invoke `FilterChain.doFilter`; blocked requests must avoid the chain and, in several cases, send HTTP 400 with the expected CSRF protection message.

## State And Persistence
State is limited to filter configuration derived during `init`: selected CSRF header name, browser user-agent patterns, and ignored method set. No files or durable state are touched.

## Dependencies And Integration Points
Depends on servlet APIs, JUnit 5, Mockito, Hadoop's `MockitoUtil.verifyZeroInteractions`, and the production `RestCsrfPreventionFilter`. It integrates with Hadoop REST HTTP security behavior by validating filter-level request gating.

## Risks
The tests verify interactions but not full response bodies or servlet-container ordering. Custom user-agent matching and comma-separated method parsing are sensitive to regex and trimming behavior. Some blocked-method tests only assert chain inactivity, so response status regressions could be missed there.

## Test Signals
Signals are `sendError(SC_BAD_REQUEST, EXPECTED_MESSAGE)` for browser requests missing the required header, `doFilter` for non-browser or ignored methods, and zero chain interactions for blocked paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/http/TestRestCsrfPreventionFilter.java -->
