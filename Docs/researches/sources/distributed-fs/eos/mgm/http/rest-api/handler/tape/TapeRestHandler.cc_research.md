## sources/distributed-fs/eos/mgm/http/rest-api/handler/tape/TapeRestHandler.cc

Purpose: wires the tape REST API routes, versioning, `.well-known` metadata, configuration gating, master-only enforcement, and centralized error mapping.

Important APIs/types/functions: `apiVersionToStr` maps `V0Dot1` and `V1`; constructor initializes well-known info, default version routes, and endpoint overrides; `initialize` creates `TapeRestApiBusiness`; `initializeStageRoutes`, `initializeArchiveinfoRoutes`, and `initializeReleaseRoutes` create action objects and register router lambdas; `isRestRequest` checks config gates; `handleRequest` rejects non-master MGM and dispatches via `HandleWithErrors`; `getAccessURLBuilder` creates `https://host:port/...`; `getWellKnownInfos` exposes discovery data.

Control flow: default version is `v1`. V1 exposes stage, archiveinfo, and release; v0.1 exposes archiveinfo/release but no stage if initialized. Actions are stored in `mActions` to keep router lambda targets alive. Requests are routed only after config-level acceptance and master check.

State and persistence: handler state is per-instantiation: config pointer, response factory, router, action vector, and well-known info. It does not persist tape state; business layer does.

Dependencies and integration points: integrates `TapeActions.hh`, `TapeRestApiBusiness`, JSON builders/jsonifiers, `Router`, `RestResponseFactory`, MGM master state, and `TapeRestApiConfig`.

Risks and test signals: route strings use both `controllerAccessURL` ending in `/` and additions like `"/" + URLPARAM_ID`, which can produce duplicate slashes; route matching and `FilesContainer` slash normalization should be tested. `mStageEnabled` is not checked in `isRestRequest`; confirm stage disabling is enforced in action code or add handler tests. Non-master returns 500 rather than redirect or 403; verify desired behavior.
