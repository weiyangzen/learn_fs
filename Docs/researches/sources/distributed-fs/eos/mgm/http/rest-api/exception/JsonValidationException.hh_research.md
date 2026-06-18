## sources/distributed-fs/eos/mgm/http/rest-api/exception/JsonValidationException.hh

Purpose: represents JSON parse or schema validation failures and optionally carries structured validation errors.

Important APIs/types/functions: constructors accept a simple message or `std::unique_ptr<ValidationErrors>`. `getValidationErrors() const` exposes a raw const pointer, while the non-const overload moves ownership out.

Control flow: JSON model builders throw this exception when request bodies are invalid. `RestResponseFactory::BadRequest(const JsonValidationException&)` inspects the first validation error when present.

State and persistence: owns an optional `ValidationErrors` vector through `unique_ptr`; moving errors out makes subsequent access null.

Dependencies and integration points: depends on `RestException` and `ValidationError.hh`. Integrated with response factory error body generation.

Risks and test signals: tests should cover malformed JSON, missing fields, structured validation errors, and repeated access after move. The overload that moves the errors can surprise callers if used before response generation.
