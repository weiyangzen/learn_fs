## sources/distributed-fs/eos/mgm/http/rest-api/router/Router.hh

Purpose: provides a small exact-pattern router for REST API handlers.

Important APIs/types/functions: `Route` stores pattern, method, and handler callback. `Router::add` appends routes. `Router::dispatch` parses request URL/method, finds matching pattern via `URLParser::matches`, checks method, and invokes callback.

Control flow: dispatch scans in registration order. If any pattern matches but method differs, throws `MethodNotAllowedException`; if no pattern matches, throws `ActionNotFoundException`.

State and persistence: stores route vector for the handler lifetime.

Dependencies and integration points: used by `TapeRestHandler` and `WellKnownHandler`; depends on common HTTP request/response, `URLParser`, and REST exceptions.

Risks and test signals: route params are not extracted by dispatch; action code likely reparses if needed. Method-not-allowed behavior depends on pattern match before method. Tests should include duplicate routes, overlapping patterns, parameter placeholders, and unknown methods.
