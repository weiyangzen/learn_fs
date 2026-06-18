## sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeWellKnownInfos.cc

Purpose: implements the container of tape REST API discovery metadata.

Important APIs/types/functions: constructor stores site name; `addEndpoint` appends a `TapeRestApiEndpoint`; `getEndpoints` returns const vector reference; `getSiteName` returns copy.

Control flow: `TapeRestHandler` constructs this object and adds default/override endpoints during initialization. `WellKnownHandler` serializes it.

State and persistence: in-memory site name and vector of endpoint objects.

Dependencies and integration points: used by tape handler and well-known response model/jsonifier.

Risks and test signals: endpoint order follows insertion order. Tests should verify default endpoint is added only when no override exists for the default version.
