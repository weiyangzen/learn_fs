## sources/distributed-fs/eos/mgm/http/rest-api/response/RestApiResponse.hh

Purpose: converts JSON-serializable models into `PlainHttpResponse` objects with status codes and optional headers.

Important APIs/types/functions: template constructors with code/model/headers; `getHttpResponse`; static `createResponse`; `void` specialization returns empty response body.

Control flow: for non-null models, creates `PlainHttpResponse`, sets header `application/type: json`, calls `mModel->jsonify`, sets body and response code. For `void`, only sets response code.

State and persistence: stores shared model, return code, and mutable header map until response creation. Allocates raw `HttpResponse*` for caller ownership.

Dependencies and integration points: used by `RestResponseFactory` for success and error responses.

Risks and test signals: header key appears to be `application/type` rather than `Content-Type`; tests should confirm clients receive expected JSON content type. Raw pointer allocation requires HTTP server ownership discipline.
