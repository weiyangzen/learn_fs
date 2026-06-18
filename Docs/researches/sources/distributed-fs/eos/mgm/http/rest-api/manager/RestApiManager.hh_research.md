## sources/distributed-fs/eos/mgm/http/rest-api/manager/RestApiManager.hh

Purpose: declares the top-level manager for REST APIs served by the MGM HTTP layer.

Important APIs/types/functions: `isRestRequest`, `getTapeRestApiConfig`, `getRestHandler`, and `getWellKnownAccessURL`; private `mTapeRestApiConfig`, `mMapAccessURLRestHandlerCreator`, and unused-looking `mWellKnownAccessURL`.

Control flow: external HTTP integration asks this manager to recognize REST requests and obtain the right handler.

State and persistence: owns tape config for process lifetime; handler instances are produced on demand.

Dependencies and integration points: depends on `RestHandler` and `TapeRestApiConfig`; concrete handlers are registered in the `.cc`.

Risks and test signals: `getTapeRestApiConfig` returns mutable raw pointer, so config mutation is unconstrained. Tests should cover lifecycle and thread-safety expectations for concurrent reads/writes.
