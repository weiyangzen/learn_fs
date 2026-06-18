## sources/distributed-fs/eos/mgm/http/rest-api/model/tape/common/ErrorModel.hh

Purpose: declares the JSON-serializable error response model for REST API failures.

Important APIs/types/functions: `ErrorModel` inherits `common::Jsonifiable<ErrorModel>`; exposes constructors, setters, getters, and optional `type`/`detail`.

Control flow: response factory creates and returns these models for 400/403/404/405/500 etc.

State and persistence: in-memory error payload only.

Dependencies and integration points: used by `RestResponseFactory` and `ErrorModelJsonifier`.

Risks and test signals: default constructor can leave title/status unset until populated; tests should avoid serializing partially initialized models unless intended.
