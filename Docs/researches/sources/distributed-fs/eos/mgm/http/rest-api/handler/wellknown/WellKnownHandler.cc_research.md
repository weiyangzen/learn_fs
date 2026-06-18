## sources/distributed-fs/eos/mgm/http/rest-api/handler/wellknown/WellKnownHandler.cc

Purpose: implements the `/.well-known/wlcg-tape-rest-api` endpoint for tape REST API discovery.

Important APIs/types/functions: constructor stores `RestApiManager` and registers routes. `handleRequest` dispatches and maps not found/method/unknown exceptions. `initializeRoutes` registers a GET handler that creates a tape handler from the manager, extracts `TapeWellKnownInfos`, verifies tape API availability through `isRestRequest`, wraps it in `GetTapeWellKnownModel`, and returns JSON.

Control flow: request enters router; route lambda re-instantiates a `TapeRestHandler` using current config, checks whether tape REST API itself is enabled, and serializes well-known versions/URLs.

State and persistence: stores manager pointer, response factory, router, and unused action vector. No persistent state; discovery info is derived dynamically from config.

Dependencies and integration points: depends on manager, tape handler, tape well-known model/jsonifier, router, response factory, and REST exceptions.

Risks and test signals: lambda uses `static_cast<TapeRestHandler*>` after requesting a handler for tape access URL; this assumes manager mapping cannot change to another handler. Availability failure returns 500 with config error detail. Tests should cover disabled tape API, endpoint overrides, method not allowed, and invalid manager return.
