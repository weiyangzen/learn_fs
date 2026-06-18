# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_general.h

Purpose: Declares service preference and log-name helper APIs.

Important APIs/types: `Services_LoadPreferences`, `Services_SavePreferences`, and `Services_GuessLogName`.

Control flow/state: Preference pointers are stored as user params on service identities by the broader identity framework.

Dependencies/integration: Used by service display, property, and log viewer code.

Risks/test signals: Header exposes only string-name `Services_GuessLogName`; the identity overload is private to the `.cpp`.
