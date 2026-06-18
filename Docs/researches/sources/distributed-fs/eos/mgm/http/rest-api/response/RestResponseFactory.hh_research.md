## sources/distributed-fs/eos/mgm/http/rest-api/response/RestResponseFactory.hh

Purpose: declares the consolidated factory for REST success and error responses.

Important APIs/types/functions: `createResponse`, `Ok`, `OkEmpty`, `Created`, `BadRequest`, `NotFound`, `MethodNotAllowed`, `Forbidden`, `NotImplemented`, `InternalError`, and private `makeError`.

Control flow: handlers/actions call factory methods after business/model work; error helpers are also used by centralized exception mapping.

State and persistence: stateless factory.

Dependencies and integration points: depends on `RestApiResponse`, `JsonValidationException`, and `ErrorModel`.

Risks and test signals: confirm `OkEmpty` returns status OK and no body, `Created` preserves custom headers, and response code enum-to-status integer conversion in error model is correct.
