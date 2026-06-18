<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-security.h -->
# sources/distributed-fs/orangefs/src/common/security/pint-security.h

## Purpose
Declares the OrangeFS security API, capability permission bits, and common error-checking macros.

## Important APIs, Types, And Functions
Defines permission bits `PINT_CAP_EXEC`, `PINT_CAP_WRITE`, `PINT_CAP_READ`, `PINT_CAP_SETATTR`, `PINT_CAP_CREATE`, `PINT_CAP_ADMIN`, `PINT_CAP_REMOVE`, `PINT_CAP_BATCH_CREATE`, and `PINT_CAP_BATCH_REMOVE`. Declares lifecycle, capability, credential, server-to-server capability, optional CA-cache, and error logging functions. Provides variadic `PINT_SECURITY_CHECK*` macros with Windows and GNU forms.

## Control Flow
Callers use initialization/finalization around security operations, initialize and sign outbound capability/credential structures, verify inbound structures, and use macros for common error-to-goto or error-to-return paths.

## State And Persistence
The header declares no state, but the APIs operate on signed PVFS structures and global security state initialized by the implementation.

## Dependencies And Integration Points
Includes PVFS config and types. It is used by real security, stubs, LDAP, UID mapping, certificate helpers, and server request validation code.

## Risks And Test Signals
Risks include macro behavior differences across compilers and permission-bit drift against server authorization logic. Tests should compile under Windows/GNU paths and verify each permission bit maps to expected access checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-security.h -->
