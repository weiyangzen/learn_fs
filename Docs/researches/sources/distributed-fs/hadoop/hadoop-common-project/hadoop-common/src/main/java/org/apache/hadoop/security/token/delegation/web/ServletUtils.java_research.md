<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/ServletUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/ServletUtils.java

Source read size: 61 lines, 2111 bytes.

## Purpose
Servlet helper for robust request parameter lookup in delegation-token HTTP handlers.

## Important APIs, Types, and Functions
The single public API is `getParameter(HttpServletRequest request, String name)`. It wraps `request.getParameter(name)` and only treats `IllegalArgumentException` specially.

## Control Flow, State, and Persistence Behavior
The method returns the request parameter value normally. If the servlet container throws `IllegalArgumentException`, usually due to invalid query-string encoding, it converts that into an `IOException` carrying the parameter name. No state is stored.

## Dependencies and Integration Points
Used by token authentication handlers when reading `op`, `delegation`, `token`, `renewer`, `service`, and related query parameters. Depends only on servlet request APIs.

## Risks and Test Signals
Risks include losing the original exception type and only covering `IllegalArgumentException`, not other container parsing failures. Test valid parameters, missing parameters, malformed encodings that trigger `IllegalArgumentException`, repeated parameters according to servlet container behavior, and callers converting the IOException to proper HTTP errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/delegation/web/ServletUtils.java -->
