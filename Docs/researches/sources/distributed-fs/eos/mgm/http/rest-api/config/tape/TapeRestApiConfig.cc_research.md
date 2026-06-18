## sources/distributed-fs/eos/mgm/http/rest-api/config/tape/TapeRestApiConfig.cc

Purpose: implements in-memory configuration for the tape REST API, including access URL, site name, activation flags, tape-enabled flag, endpoint-to-URL overrides, host alias, xrootd HTTP port, and stage enablement.

Important APIs/types/functions: constructors default `mAccessURL` to `/api/` or accept a custom access URL. Setters/getters exist for site name, activated state, tape-enabled state, host alias, endpoint mapping, XrdHttp port, access URL, and stage-enabled state.

Control flow: setters mutate the relevant field; string/map fields take write locks and getters take read locks. Atomic bool/port fields are read/written directly. `getAccessURL` returns a const reference without locking because the access URL is immutable after construction.

State and persistence: configuration is purely process-local and not persisted here. Values are populated by `RestApiManager`/MGM configuration code elsewhere and consumed when handlers are instantiated.

Dependencies and integration points: uses `common::RWMutex` lock guards and atomics. `TapeRestHandler` consults this object for request acceptance, route construction, `.well-known` endpoint URLs, host alias, port, and site name.

Risks and test signals: `mXrdHttpPort` is atomic but not initialized in the header, so tests should verify config population before `.well-known` URL construction. Endpoint map copies are protected, but no validation is performed on version strings or URLs.
