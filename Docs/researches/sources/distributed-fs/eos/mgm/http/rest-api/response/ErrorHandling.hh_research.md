## sources/distributed-fs/eos/mgm/http/rest-api/response/ErrorHandling.hh

Purpose: centralizes exception-to-HTTP-response mapping for REST handlers.

Important APIs/types/functions: template `HandleWithErrors(ResponseFactory&, Fn)` catches `NotFoundException`, `MethodNotAllowedException`, `ForbiddenException`, `NotImplementedException`, generic `RestException`, and unknown exceptions.

Control flow: handler passes a lambda that may throw; helper logs and returns response factory outputs. Specific exceptions map to 404, 405, 403, 501; generic REST and unknown map to 500.

State and persistence: stateless function template.

Dependencies and integration points: used by `TapeRestHandler::handleRequest`; depends on response factory methods and REST exception hierarchy.

Risks and test signals: `JsonValidationException` currently derives from `RestException` but is not caught before generic `RestException` here, so if action code does not catch it, invalid JSON becomes 500. Tests should verify action-level handling or add a catch.
