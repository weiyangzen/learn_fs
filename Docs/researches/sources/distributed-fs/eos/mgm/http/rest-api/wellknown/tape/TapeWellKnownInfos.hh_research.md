## sources/distributed-fs/eos/mgm/http/rest-api/wellknown/tape/TapeWellKnownInfos.hh

Purpose: declares the discovery metadata container for the tape REST API.

Important APIs/types/functions: `Endpoints` alias, constructor, `addEndpoint`, `getEndpoints`, `getSiteName`, `mSiteName`, and `mEndpoints`.

Control flow: filled during handler construction, then read by `.well-known` model/jsonifier.

State and persistence: in-memory metadata only.

Dependencies and integration points: owns `TapeRestApiEndpoint` objects.

Risks and test signals: raw pointer consumers of this object must respect handler lifetime. Site name is stored but current jsonifier serializes only versions/URLs, so tests should confirm whether site metadata is expected.
