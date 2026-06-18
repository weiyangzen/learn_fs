# sources/distributed-fs/orangefs/src/client/windows/client-service/cert.h

## Purpose
This header declares Windows client-service certificate support: OpenSSL lifecycle hooks and public functions for deriving OrangeFS credentials from proxy or user certificates.

## Important APIs, types, and functions
It exposes `openssl_init`, `openssl_cleanup`, `get_proxy_cert_credential`, and `get_user_cert_credential`. Both credential functions accept a Windows user token handle, username, output `PVFS_credential`, and output certificate expiration pointer.

## Control flow
Callers initialize OpenSSL before certificate use, call one of the credential loaders according to user/security mode, cache or consume the returned credential and expiration, and eventually call `openssl_cleanup` during shutdown.

## State and persistence behavior
The header itself has no state, but its APIs allocate credential fields and an `ASN1_UTCTIME` expiration that callers must clean according to the service's credential/cache ownership rules.

## Dependencies and integration points
It includes OpenSSL ASN.1 definitions, `pvfs2.h`, and `client-service.h`, so it is bound to Windows `HANDLE` types and OrangeFS credential definitions. `dokan-interface.c` includes this header for user-mode credential lookup.

## Risks and edge cases
The header does not document ownership of `expires` or initialized credential fields. It also exposes OpenSSL types to all consumers, increasing ABI coupling.

## Test signals
Compile consumers with the target OpenSSL version and verify function prototypes match `cert.c`. Add ownership tests around returned expiration and credential cleanup in user-cache paths.
