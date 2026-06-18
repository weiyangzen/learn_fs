# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_create.h

Purpose: Declares service creation task data and UI entry point.

Important APIs/types: `SVC_CREATE_PARAMS` stores target server, service name, command, params, notifier, log file, service type, run-now flag, and cron schedule. `Services_Create(LPIDENT)` opens the creation UI.

Control flow/state: The create dialog fills the packet and passes it to `taskSVC_CREATE`.

Dependencies/integration: Uses `AFSSERVICETYPE`, `SYSTEMTIME`, and `LPIDENT` from the broader OpenAFS Windows manager framework.

Risks/test signals: Verify field buffer sizes match BOS service creation API expectations.
