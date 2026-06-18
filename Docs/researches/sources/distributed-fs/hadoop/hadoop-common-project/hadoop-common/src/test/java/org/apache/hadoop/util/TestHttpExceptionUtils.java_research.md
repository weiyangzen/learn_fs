# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestHttpExceptionUtils.java

Purpose: JUnit coverage for `HttpExceptionUtils`, the helper that serializes server-side exceptions into HTTP/Jersey JSON responses and reconstructs/normalizes failed HTTP client responses.

Important APIs and types: tests call `createServletExceptionResponse(HttpServletResponse,int,Exception)`, `createJerseyExceptionResponse(Response.Status,Exception)`, and `validateResponse(HttpURLConnection,int)`. They assert the JSON envelope fields `ERROR_JSON`, `ERROR_CLASSNAME_JSON`, `ERROR_EXCEPTION_JSON`, and `ERROR_MESSAGE_JSON`, and use Jackson `ObjectMapper`, Jersey `Response`, servlet response mocks, and `LambdaTestUtils`.

Control flow: the servlet test writes to a mocked response writer, verifies status/content type, and parses JSON. The Jersey test inspects status, metadata, and entity map. Validation tests cover expected status passthrough, no error stream, non-JSON error stream, known exception class reconstruction, unknown exception fallback, and class names that are not exceptions.

State and persistence: no persistent state; state is in mock responses, byte-array streams, and JSON maps. The stream position matters because `validateResponse` consumes the error stream once.

Dependencies and integration points: integrates HTTP status handling, Jackson parsing, Jersey media types, servlet writers, reflection-based exception loading, and Hadoop test intercept utilities.

Risks: regressions may leak raw parser errors, lose the original remote exception class/message, throw non-IOException types unexpectedly, or fail when the remote class is absent/non-Throwable. Test signals are precise exception type/message assertions and response metadata verification.
