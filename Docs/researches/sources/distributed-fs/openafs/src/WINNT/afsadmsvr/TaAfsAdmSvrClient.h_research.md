# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClient.h

Purpose: public client-library API for applications that talk to the OpenAFS Windows administration server.

Important APIs/types/functions: defines `ADMINAPI`, notification messages `WM_ASC_NOTIFY_OBJECT` and `WM_ASC_NOTIFY_ACTION`, list helper prototypes, admin-server open/close, credentials, local cell/error translation, cell/object operations, refresh, random key, fast cache getters, critical-section access, notifications, action queries/listeners, and user/group administration functions.

Control flow: consumers open an admin server, obtain credentials, open cells, query/mutate objects, optionally register window notifications, then close cells and server connections.

State/persistence: header has no state. Implementations maintain process-global binding, cache, ping/callback threads, and listener lists.

Dependencies/integration: includes `TaAfsAdmSvr.h` and generated IDL types. Intended for Win32 GUI/admin tools using HWND notifications.

Risks/test signals: API uses fixed buffers and many optional `ULONG *pStatus` outputs; callers must free returned lists with matching `asc_*Free` functions. Tests should compile representative consumers and verify C++ default arguments, notification message contracts, and free/ownership rules.
