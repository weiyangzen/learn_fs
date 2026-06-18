## sources/distributed-fs/eos/mgm/http/rest-api/handler/RestHandler.hh

Purpose: declares the abstract base class for REST HTTP handlers.

Important APIs/types/functions: pure virtual `handleRequest(HttpRequest*, const VirtualIdentity*)`; virtual `isRestRequest`; `getEntryPointURL`; protected `mEntryPointURL`; private entrypoint verifier.

Control flow: `RestApiManager` creates concrete handlers and calls `isRestRequest`/`handleRequest` depending on URL routing.

State and persistence: no persistent storage beyond entrypoint string.

Dependencies and integration points: depends on common HTTP request/response classes, `VirtualIdentity`, and XrdHttp handler types. Extended by tape and well-known handlers.

Risks and test signals: concrete handlers own raw `HttpResponse*` return semantics; tests should confirm response ownership expectations at the higher HTTP server layer.
