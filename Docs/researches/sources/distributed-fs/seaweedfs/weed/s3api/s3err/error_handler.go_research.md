# sources/distributed-fs/seaweedfs/weed/s3api/s3err/error_handler.go

Purpose: shared HTTP response writer for S3 XML success/error responses. It standardizes request IDs, content headers, CORS fallback behavior, XML encoding, audit logging, and the default not-found route behavior.

Important APIs/types: `WriteAwsXMLResponse`, `WriteXMLResponse`, `WriteEmptyResponse`, `WriteErrorResponse`, `WriteErrorResponseWithMessage`, `EncodeXMLResponse`, `WriteResponse`, and `NotFoundHandler`. `MimeXML` is exported as the XML content type; `mimeNone` suppresses content type.

Control flow: success helpers encode XML and call `WriteResponse`. Error helpers ensure a request ID, pull mux `bucket`/`object` vars, normalize a leading slash from object, look up `APIError`, build `RESTErrorResponse`, optionally override message, write XML, and post audit log. `setCommonHeaders` always sets `x-amz-request-id` and `Accept-Ranges`, and conditionally adds permissive CORS headers for service-level requests when an `Origin` header exists. `WriteResponse` sets content length/type, writes status/body, logs at verbosity 4, and flushes the writer.

State and persistence behavior: no local persistence. It mutates HTTP response headers and triggers audit emission through `PostLog`.

Dependencies and integration points: uses AWS SDK `xmlutil` for AWS XML building, Gorilla mux for URL vars, SeaweedFS `request_id`, and audit logging in this package. All S3 handlers rely on this layer for consistent client-visible error shape.

Risks: `WriteResponse` type-asserts `w.(http.Flusher)` and will panic for a ResponseWriter that does not implement `http.Flusher`; `httptest.ResponseRecorder` does implement it in modern Go, but wrappers may not. `EncodeXMLResponse` ignores encoder errors. Service-level CORS fallback is broad (`*` plus credentials), while bucket-level requests preserve middleware decisions. `GetAPIError` returns a zero `APIError` for unmapped codes, so new `ErrorCode` constants must be mapped.

Test signals: `error_handler_test.go` verifies that request IDs already in context are reused in both header and XML body for error responses.
