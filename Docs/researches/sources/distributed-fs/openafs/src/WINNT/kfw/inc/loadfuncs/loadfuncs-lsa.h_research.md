# sources/distributed-fs/openafs/src/WINNT/kfw/inc/loadfuncs/loadfuncs-lsa.h

## Purpose

This header declares dynamic bindings to Windows LSA/security APIs from `secur32.dll` and `advapi32.dll`. It supports integration with the Windows Local Security Authority, especially locating authentication packages and interacting with logon-session data.

## Important APIs, Types, and Functions

- `SECUR32_DLL` names `secur32.dll`; `ADVAPI32_DLL` names `advapi32.dll`.
- `LsaConnectUntrusted` opens an untrusted LSA connection.
- `LsaLookupAuthenticationPackage` resolves an authentication package ID.
- `LsaCallAuthenticationPackage` sends package-specific requests.
- `LsaFreeReturnBuffer` releases buffers returned by LSA.
- `LsaNtStatusToWinError` maps `NTSTATUS` to Win32 error codes.
- `LsaGetLogonSessionData` retrieves logon session metadata.

## Control Flow

The expected sequence is to dynamically load the security DLL, bind LSA functions, connect to LSA, look up an authentication package, call into it, translate errors as needed, and release returned buffers. The header itself only provides function-pointer typedefs.

## State and Persistence Behavior

The header stores no state. The external LSA APIs operate on process handles, authentication-package state, return buffers, and OS logon sessions. Callers must close or release OS resources using the appropriate Windows APIs and `LsaFreeReturnBuffer`.

## Dependencies and Integration Points

Depends on `loadfuncs.h` and Windows security types such as `NTSTATUS`, `PLSA_STRING`, `PSECURITY_LOGON_SESSION_DATA`, `PLUID`, and `HANDLE`. It likely integrates Kerberos credential import/export with MSLSA logon sessions.

## Risks

- LSA calls are privilege- and policy-sensitive; behavior differs by Windows version, logon type, and process token.
- Return buffers must be freed with LSA APIs, not normal heap free.
- Authentication package request structures are not declared here, so type mismatch risk sits at call sites.
- Dynamic loading can fail on older or restricted systems, and callers need fallback behavior.

## Test Signals

Tests should cover missing-symbol handling, `NTSTATUS` to Win32 conversion, successful untrusted LSA connection on supported Windows, and proper buffer release. Integration tests should use non-destructive read-only logon-session queries where possible.
