## sources/distributed-fs/eos/mgm/http/rest-api/manager/RestApiManager.cc

Purpose: implements the REST API manager that owns tape REST configuration and creates handlers based on request URL prefixes.

Important APIs/types/functions: constructor creates `TapeRestApiConfig`, registers a factory for its access URL and one for `/.well-known/`; `isRestRequest` asks the matching handler whether it accepts the URL; `getTapeRestApiConfig` returns the mutable config pointer; `getRestHandler` finds the first access URL whose prefix matches; `getWellKnownAccessURL` returns `/.well-known/`.

Control flow: no handler instances are cached; a new handler is created for each query/dispatch path. Prefix matching is performed through `URLParser::startsBy`.

State and persistence: owns config and a map of URL prefixes to handler factories. No persistent storage.

Dependencies and integration points: integrates `TapeRestHandler`, `WellKnownHandler`, `TapeRestApiConfig`, and `URLParser`.

Risks and test signals: `std::map` iteration order controls prefix selection; overlapping prefixes should be tested. Recreating handlers per request rebuilds routes and well-known info each time, so performance and config consistency should be monitored.
