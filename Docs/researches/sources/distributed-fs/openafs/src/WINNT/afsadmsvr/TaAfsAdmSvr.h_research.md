# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvr.h

Purpose: common public header for the OpenAFS Windows administration server executable and client library.

Important APIs/types/functions: includes RPC/Windows/localization/generated admin-server headers and defines program name, command-line keywords (`Timed`, `Manual`, `Users`, `Volumes`, `Debug`), default RPC namespace entry name, and default endpoint `1025`.

Control flow: admin server startup and client binding code use these constants to decide auto-shutdown/manual startup, auto-open scope, debug behavior, and binding fallback.

State/persistence: no state in the header. The endpoint and entry name define external binding identity.

Dependencies/integration: pulls in generated `iTaAfsAdmSvr.h`, common list helpers, `TaLocale`, and optionally app-library declarations.

Risks/test signals: default endpoint collisions or namespace export failures affect all clients. Tests should verify server command-line parsing, fallback endpoint binding, and generated header inclusion order.
