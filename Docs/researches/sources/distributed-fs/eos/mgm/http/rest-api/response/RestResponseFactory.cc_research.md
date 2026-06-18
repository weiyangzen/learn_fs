## sources/distributed-fs/eos/mgm/http/rest-api/response/RestResponseFactory.cc

Purpose: implements consolidated REST response factory error helpers.

Important APIs/types/functions: `makeError` creates `ErrorModel`, attaches `ErrorModelJsonifier`, and returns `RestApiResponse<ErrorModel>`. Public helpers implement `BadRequest`, `BadRequest(JsonValidationException)`, `NotFound`, `MethodNotAllowed`, `Forbidden`, `NotImplemented`, and `InternalError`.

Control flow: each helper maps a semantic error to an HTTP response code and title. Validation bad request prefers first structured validation error, otherwise exception text.

State and persistence: factory is stateless; responses own models by shared pointer.

Dependencies and integration points: used by REST handlers and `HandleWithErrors`; depends on tape jsonifiers for error serialization.

Risks and test signals: error detail is serialized without JSON escaping by `ErrorModelJsonifier`. `BadRequest(JsonValidationException)` only reports one validation error. Tests should verify exact status codes and JSON body shape.
