## sources/distributed-fs/eos/mgm/http/rest-api/json/builder/ValidationError.hh

Purpose: provides small structures for structured JSON validation errors.

Important APIs/types/functions: `ValidationError` stores `fieldName` and `reason`; `ValidationErrors` owns a vector of `unique_ptr<ValidationError>` and exposes `addError`, `getErrors`, and `hasAnyError`.

Control flow: validators/builders can accumulate errors and pass them into `JsonValidationException`.

State and persistence: in-memory ownership of error objects only.

Dependencies and integration points: used by `JsonValidationException` and `RestResponseFactory::BadRequest` for client error details.

Risks and test signals: only the first validation error is emitted by the current response factory. Tests should verify ordering, empty error lists, and move-only behavior.
