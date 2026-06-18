## sources/distributed-fs/eos/mgm/http/rest-api/handler/tape/TapeRestHandler.hh

Purpose: declares the concrete REST handler for WLCG tape API requests.

Important APIs/types/functions: public constructor, `handleRequest`, `isRestRequest`, `getAccessURLBuilder`, and `getWellKnownInfos`. Private `ApiVersion`, `DEFAULT_API_VERSION`, route initialization helpers, well-known helpers, response factory, config pointer, router, action storage, and well-known info.

Control flow: the handler owns route initialization and delegates request execution to action objects via `Router`.

State and persistence: holds handler-local routing/action/discovery state; config is borrowed by pointer and must outlive the handler.

Dependencies and integration points: depends on `RestHandler`, tape business interface, `Router`, `Action`, `RestResponseFactory`, `TapeRestApiConfig`, `URLBuilder`, and `TapeWellKnownInfos`.

Risks and test signals: tests should verify object lifetime of action lambdas, default endpoint generation, config gating, and behavior when endpoint override mapping contains unsupported versions.
