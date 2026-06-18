## sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeRestApiEndpoint.cc

Purpose: implements a simple value object describing one tape REST API endpoint/version pair for discovery responses.

Important APIs/types/functions: constructor stores URI and version; `getUri` and `getVersion` return copies.

Control flow: `TapeWellKnownInfos::addEndpoint` creates these objects; jsonifier reads them for `.well-known` output.

State and persistence: in-memory URI/version strings only.

Dependencies and integration points: used exclusively by `TapeWellKnownInfos` and well-known JSON serialization.

Risks and test signals: no validation or escaping is done here; tests should validate endpoint override values before JSON output.
