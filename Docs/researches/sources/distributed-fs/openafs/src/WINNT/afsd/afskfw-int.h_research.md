# sources/distributed-fs/openafs/src/WINNT/afsd/afskfw-int.h

## Purpose

`afskfw-int.h` is an internal Windows Kerberos for Windows integration header. It centralizes includes, constants, dynamic service-control function pointer types, token/cache mapping structures, and prototypes for KFW/MSLSA/AFS token operations used by AFSD-adjacent authentication code.

## Important APIs, Types, and Functions

- Includes Windows, optional MS2MIT LSA security headers, Winsock/process/time headers, AFS standards, Kerberos 5, and RXKAD.
- Service dynamic-load typedefs include `FP_OpenSCManagerA`, `FP_OpenServiceA`, `FP_QueryServiceStatus`, and `FP_CloseServiceHandle`.
- Constants include `KRB5_DEFAULT_LIFE`, `LSA_CCTYPE`, `LSA_CCNAME`, `REALM_SZ`, and fallback `KTC_*` error codes.
- `struct textField` models prompted user input fields with buffer, length, label, default, and echo behavior.
- `struct principal_ccache_data` tracks principal-to-ccache records, whether imported from LSA, expiration, and renew behavior.
- `struct cell_principal_map` maps AFS cell names to principals with an active flag.
- Prototypes cover service status (`GetServiceStatus`), error reporting (`KFW_AFS_error`, `KFW_error`), cache operations (`KFW_get_ccache`, `KFW_import_ccache_data`), Kerberos lifecycle (`KFW_kinit`, `KFW_renew`, `KFW_destroy`), MSLSA import (`KFW_ms2mit`, `MSLSA_IsKerberosLogon`, `KFW_get_default_mslsa_import`), AFS token operations (`KFW_AFS_unlog`, `KFW_AFS_klog`), realm/lifetime/DES helpers (`afs_realm_of_cell`, `KFW_get_default_lifetime`, `KFW_enable_DES`).

## Control Flow

The header has no executable control flow, but it defines the operation set expected by authentication flows: discover service/login state, locate or acquire a Kerberos credential cache, optionally import MSLSA tickets, obtain or renew Kerberos credentials, convert them into AFS tokens, and destroy/unlog credentials as requested.

## State and Persistence Behavior

Structures describe linked-list process memory state for principal caches and cell mappings. Persistent state is external: Kerberos credential caches, MSLSA logon sessions, AFS tokens, service state, and registry/default configuration read by implementation files.

## Dependencies and Integration Points

This header is tightly coupled to MIT Kerberos (`krb5_context`, `krb5_principal`, `krb5_ccache`, `krb5_deltat`), AFS config/cell structures, RXKAD security, Windows service APIs, and optional MS2MIT LSA APIs. It bridges Windows logon credentials to AFS token acquisition.

## Risks

- It is an internal header with broad includes and many prototypes, so include-order or macro conflicts with Windows/Kerberos headers are likely.
- Fallback `KTC_*` definitions can diverge from canonical token error definitions if upstream values change.
- DES enablement support (`KFW_enable_DES`) is legacy-sensitive and should be constrained by modern security policy.
- Linked-list structures rely on implementation-owned allocation and lifetime discipline not visible in the header.

## Test Signals

- Build matrix tests should cover `USE_MS2MIT` on/off and supported `_WIN32_WINNT` values.
- Authentication integration tests should cover MSLSA import, explicit ccache selection, kinit/renew/destroy, AFS klog/unlog, expired credentials, and cell realm discovery.
- Security tests should verify default lifetime, DES behavior, and error translation for `KTC_*` and Kerberos failures.
