# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSMDCFilter.java

## Purpose
`KMSMDCFilter.java` captures request context for the current KMS request and exposes it through static thread-local accessors used by exception and audit code.

## Important APIs, Types, and Functions
The private `Data` holder stores UGI, HTTP method, full URL, and remote client address. Static methods `getUgi`, `getMethod`, `getURL`, and `getRemoteClientAddress` read the current thread context. `setContext` is visible for testing.

## Control Flow
`doFilter` clears any stale context, obtains the request UGI from `HttpUserGroupInformation`, builds a URL including query string, stores context, invokes the next filter/servlet, and clears context in `finally`.

## State and Persistence
State is request-scoped in a `ThreadLocal`. It is explicitly removed before and after chain execution to prevent leakage across reused servlet threads.

## Dependencies and Integration Points
It depends on Servlet APIs, `HttpUserGroupInformation`, and Hadoop UGI. `KMSExceptionsProvider` uses its context for audit and warning logs.

## Risks
If this filter is not invoked, exception logs lose request context. It casts to `HttpServletRequest`, so it assumes HTTP traffic. Filter ordering matters: authentication should run first so `HttpUserGroupInformation.get()` is populated.

## Test Signals
Tests should verify context population with query strings, remote address capture, cleanup after success and exception, null accessors outside a request, and filter ordering assumptions with authentication.
