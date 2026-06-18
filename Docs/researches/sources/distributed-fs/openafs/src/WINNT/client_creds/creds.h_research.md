# sources/distributed-fs/openafs/src/WINNT/client_creds/creds.h

Purpose: declares credential and service helper APIs used by the credentials UI, wizard, tray, and network-change code.

Important APIs: service helpers (`IsServiceRunning`, `IsServicePersistent`, `IsServiceConfigured`), token lifecycle (`GetCurrentCredentials`, `DestroyCurrentCredentials`, `ObtainNewCredentials`), cell/gateway lookup (`GetDefaultCell`, `GetGatewayName`), and dynamic library lifecycle (`Creds_OpenLibraries`, `Creds_CloseLibraries`).

Control flow: no implementation. It defines the public credential-management surface for `creds.cpp`.

State/persistence: callers should assume these functions may read registry/service state and mutate global credential state.

Dependencies/integration: C linkage guard allows inclusion from C or C++ modules; signatures use Win32 string types.

Risks: API side effects are not visible from prototypes. `ObtainNewCredentials` accepts raw password text and a `Silent` flag, so callers must manage UI/error policy and sensitive data lifetime.

Test signals: link coverage for both C and C++ users, and callers correctly handling nonzero OpenAFS/Kerberos error codes.
