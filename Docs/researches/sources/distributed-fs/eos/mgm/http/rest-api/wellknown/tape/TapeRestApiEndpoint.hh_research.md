## sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeRestApiEndpoint.hh

Purpose: declares the endpoint/version value object for tape REST API discovery.

Important APIs/types/functions: `TapeRestApiEndpoint(uri, version)`, `getUri`, `getVersion`, private `mUri` and `mVersion`.

Control flow: endpoints are accumulated in `TapeWellKnownInfos` and serialized in discovery responses.

State and persistence: in-memory value object.

Dependencies and integration points: used by `TapeWellKnownInfos`.

Risks and test signals: getters return copies, which is simple but unnecessary for hot paths; no behavioral risk beyond validation at construction sites.
