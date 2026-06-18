## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/ErrorModel.cc

Purpose: implements the RFC 7807-like error model used by REST error responses.

Important APIs/types/functions: constructors set title/status/detail; setters for type/title/status/detail; getters return optional type/detail and scalar fields.

Control flow: `RestResponseFactory::makeError` constructs and jsonifies `ErrorModel` for HTTP error responses.

State and persistence: stores title, status, optional detail, and optional type in memory.

Dependencies and integration points: paired with `ErrorModelJsonifier` and response factory.

Risks and test signals: string fields are serialized manually by `ErrorModelJsonifier`; tests should include quotes/newlines in details and verify RFC 7807 content expectations.
