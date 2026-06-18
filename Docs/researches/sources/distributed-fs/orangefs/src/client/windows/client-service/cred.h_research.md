# sources/distributed-fs/orangefs/src/client/windows/client-service/cred.h

## Purpose
This header declares the Windows client-service credential helper API.

## Important APIs, types, and functions
Public declarations include `init_credential`, `cleanup_credential`, `credential_in_group`, and `get_system_credential`. Commented declarations document disabled `credential_add_group` and `credential_set_timeout` helpers.

## Control flow
Callers allocate a `PVFS_credential`, initialize it through `init_credential` or `get_system_credential`, pass it to OrangeFS filesystem calls, then release dynamic fields with `cleanup_credential` or `PINT_cleanup_credential` as appropriate.

## State and persistence behavior
The API initializes heap-owned fields inside caller-provided structs. Persistent key/certificate reads are controlled by the implementation and global options, not by this header.

## Dependencies and integration points
It includes OrangeFS credential and request protocol definitions. Config, certificate, user-cache, and Dokan code use the declarations to construct request credentials.

## Risks and edge cases
The header does not declare `sign_credential` even though it is externally linkable in `cred.c`; this limits intended public API but leaves a non-static symbol. Ownership expectations around certificate buffers are not documented.

## Test signals
Compile all service modules against this header with warnings for missing prototypes, and add API-level tests that pair every successful initialization with cleanup.
