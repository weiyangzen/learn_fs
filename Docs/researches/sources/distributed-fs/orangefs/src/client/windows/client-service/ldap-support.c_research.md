# sources/distributed-fs/orangefs/src/client/windows/client-service/ldap-support.c

## Purpose
`ldap-support.c` implements optional LDAP-backed mapping from Windows user names to OrangeFS credentials. It connects to an LDAP server, searches configured attributes, validates numeric UID/GID values, and builds a `PVFS_credential`.

## Important APIs, Types, And Functions
Public functions are `PVFS_ldap_init`, `PVFS_ldap_cleanup`, and `get_ldap_credential`. `check_number` validates LDAP attribute values before conversion. The global `timeout` gives LDAP searches a 15-second bound. The implementation reads LDAP configuration from global `goptions`.

## Control Flow
Initialization calls Netscape-style LDAP SSL setup and disables certificate verification. Credential lookup handles `SYSTEM` specially by returning the system credential, initializes an LDAP connection with optional SSL, sets protocol version 3, binds with configured DN/password or anonymously, constructs a filter from configured object class, naming attribute, and user name, requests UID/GID attributes, and scans the first result entry. If both numeric values are present, it calls `init_credential`.

## State And Persistence
The file stores no durable state. LDAP library initialization is process-global, and each credential lookup uses transient connection/search/result objects. Credentials may later be cached by `user-cache.c`.

## Dependencies And Integration Points
It depends on Windows, LDAP/LDAP SSL headers, `cred.h`, `ldap-support.h`, `client-service.h`, and reporting via `report_error`. The Dokany credential path currently has LDAP mode commented out, and service initialization also comments out LDAP init/cleanup, so this implementation appears dormant unless re-enabled.

## Risks And Test Signals
LDAP filters interpolate `user_name` without escaping, creating LDAP injection risk if external names can contain filter metacharacters. `LDAPSSL_VERIFY_NONE` disables server certificate verification. `attrs[0]` and `attrs[1]` are heap-allocated with fixed 32-byte buffers and `strncpy` may leave them unterminated. `results` is not initialized before use. There are no listed client tests for LDAP mode; coverage would require configured LDAP integration tests and credential cache interaction checks.
