## sources/distributed-fs/eos/mgm/http/rest-api/handler/wellknown/WellKnownHandler.hh

Purpose: declares the REST handler for `.well-known` discovery routes.

Important APIs/types/functions: constructor, `handleRequest`, private `initializeRoutes`, manager pointer, response factory, router, and action vector.

Control flow: extends `RestHandler` and routes discovery requests through `Router`.

State and persistence: no persistent storage; keeps a non-owning `RestApiManager` pointer.

Dependencies and integration points: includes `RestHandler`, `RestResponseFactory`, `Router`, `Action`, and `TapeRestHandler`; forward declares `RestApiManager`.

Risks and test signals: manager pointer lifetime is critical. The `mActions` vector is present but unused in this implementation, so tests should focus on router behavior rather than action lifetime.
