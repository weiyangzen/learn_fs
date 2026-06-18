# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMSMDCFilter.java

## Purpose
`TestKMSMDCFilter.java` validates request-context lifecycle behavior for `KMSMDCFilter`, ensuring method, URL, remote address, and UGI context are populated during filtering and cleared afterward.

## Important APIs, Types, and Functions
- `setUp()` creates a `KMSMDCFilter`, mocked `HttpServletRequest`/`HttpServletResponse`, and clears the static context.
- `testFilter()` stubs request method, URL, and remote address, then invokes `doFilter()`.
- The inline `FilterChain` asserts that `KMSMDCFilter.getRemoteClientAddress()`, `getMethod()`, and `getURL()` are set while the downstream chain runs.
- `checkMDCValuesAreEmpty()` asserts all context getters, including `getUgi()`, return null before and after filtering.

## Control Flow and State
The filter sets thread-local or static MDC context before invoking the chain and clears it in cleanup logic after the chain returns. The test verifies both sides of that lifecycle.

## Dependencies and Integration Points
The test uses Mockito, servlet `FilterChain`, and KMS MDC accessors. The context is used by KMS request logging, auditing, and diagnostics.

## Risks and Edge Cases
The test does not throw from the chain, so exception-path cleanup should be covered elsewhere or by inspecting filter implementation. Static context reset in setup is important to avoid cross-test contamination.

## Test Signals
This is a focused signal that KMS per-request diagnostic context does not leak across requests.
