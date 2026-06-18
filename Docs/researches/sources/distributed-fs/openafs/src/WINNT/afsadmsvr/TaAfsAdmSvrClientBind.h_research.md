# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientBind.h

Purpose: internal client-library header for admin-server binding helpers.

Important APIs/types/functions: declares `BindToAdminServer()`, `UnbindFromAdminServer()`, `ForkNewAdminServer()`, and `ResolveAddress()`.

Control flow: used by `asc_AdminServerOpen()` and `asc_AdminServerClose()` to establish or release the RPC binding.

State/persistence: no header state; implementation mutates the global RPC binding and may launch a server process.

Dependencies/integration: expects `ADMINAPI`, `LPCTSTR`, `UINT_PTR`, and status types from enclosing client headers.

Risks/test signals: this is internal but affects connection reliability. Compile tests should catch include-order dependencies and signature drift from implementation.
