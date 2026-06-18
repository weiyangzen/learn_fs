# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/conf/TestConfServlet.java

## Purpose

`TestConfServlet` validates the HTTP-facing `ConfServlet` configuration dump endpoint. It exercises content negotiation, property filtering by request parameter, JSON/XML serialization, not-found behavior, invalid output formats, and masking of sensitive configuration values before they reach the servlet response.

## Important APIs and types

- `ConfServlet.parseAcceptHeader(HttpServletRequest)` maps `Accept` headers to `ConfServlet.FORMAT_XML` or `ConfServlet.FORMAT_JSON`.
- `ConfServlet.writeResponse(Configuration, Writer, String)` serializes a Hadoop `Configuration` as XML or JSON and throws `ConfServlet.BadFormatException` for unsupported formats.
- `ConfServlet.doGet(...)` reads `HttpServer2.CONF_CONTEXT_ATTRIBUTE` from the servlet context, consults request parameter `name`, and writes or errors through `HttpServletResponse`.
- Test helpers build `Configuration` instances with normal keys and YARN SQL username/password keys that should be redacted.
- Mockito provides servlet request/response/context doubles; Jetty `JSON.parse` and secure DOM parsing validate response structure.

## Control flow

`initTestProperties` seeds shared normal property maps, accepted content-type mappings, and sensitive properties. `testParseHeaders` loops over representative `Accept` values and checks the servlet's selected format.

`verifyGetProperty` initializes a servlet with a mocked context, sets the request `Accept` header and `name` parameter, invokes `doGet`, and inspects the captured response writer. A null or empty `name` expects all normal properties; a known property expects only that property; an unknown property expects `sendError(SC_NOT_FOUND, ...)`.

`testWriteJson` and `testWriteXml` bypass the servlet request path and directly validate `writeResponse` output. JSON is parsed into the expected `"properties"` array and XML is parsed through `XMLUtils.newSecureDocumentBuilderFactory`. `testBadFormat` ensures unsupported formats produce no partial output. `verifyReplaceProperty` repeats the servlet path for sensitive keys and checks that the original secret value is absent.

## State and persistence behavior

The tests are in-memory. The servlet uses a `Configuration` stored on the servlet context; response content is accumulated in `StringWriter`. Static maps are mutated once before all tests. No filesystem persistence or external server is started.

## Dependencies and integration points

The file integrates `ConfServlet` with `HttpServer2`'s configuration context attribute, servlet APIs, Hadoop `Configuration`, Guava HTTP header constants and string helpers, Jetty JSON parsing, secure XML parsing utilities, JUnit 5, and Mockito. It is a regression surface for admin web UI/configuration endpoints where exposing or filtering configuration values is security-sensitive.

## Risks and edge cases

- Header parsing currently treats unknown, null, plain text, and XML-ish headers as XML; clients with more complex `Accept` negotiation are not covered.
- The property filtering assertions use substring checks, so formatting changes could produce false positives if one key/value appears inside another.
- Redaction checks only verify that the original sensitive value is absent, not the exact replacement token in every output format.
- The mocked servlet setup does not validate actual HTTP content type headers, response status on successful requests, or container lifecycle details.

## Test signals

Strong signals are the matrix of XML/JSON output, null/empty/specific/missing property names, direct JSON/XML parse validation, explicit bad-format rejection, and sensitive-value absence checks for both output formats. Gaps include weighted `Accept` headers, malformed XML/JSON output handling, exact redaction token validation, and end-to-end servlet container tests.
