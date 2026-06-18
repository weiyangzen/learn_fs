## sources/distributed-fs/eos/mgm/http/webdav/PropPatchResponse.hh

Purpose: declares the WebDAV PROPPATCH response builder.

Important APIs/types/functions: constructor stores `VirtualIdentity*`; `BuildResponse` creates the XML response.

Control flow: used by `WebDAVHandler` for PROPPATCH requests.

State and persistence: identity pointer is stored, but implementation does not persist properties.

Dependencies and integration points: inherits `WebDAVResponse`; includes RapidXML and mapping dependencies.

Risks and test signals: if future implementation persists properties, tests must add permission checks and atomicity semantics required by WebDAV PROPPATCH.
