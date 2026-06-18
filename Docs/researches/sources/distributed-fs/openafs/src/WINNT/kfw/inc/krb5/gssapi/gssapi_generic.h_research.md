## sources/distributed-fs/openafs/src/WINNT/kfw/inc/krb5/gssapi/gssapi_generic.h

Purpose: Compatibility header exporting deprecated MIT generic GSS name-type OID variables.

Important APIs/types/functions: Includes `<gssapi/gssapi.h>` and declares `gss_nt_user_name`, `gss_nt_machine_uid_name`, `gss_nt_string_uid_name`, `gss_nt_service_name_v2`, `gss_nt_service_name`, and `gss_nt_exported_name`.

Control flow: No runtime logic. Consumers pass these OID variables to GSS name import/compare/display APIs.

State and persistence: OID variables refer to implementation-owned static storage. Callers must not free them.

Dependencies and integration points: Bridges old MIT names to RFC 2744 OID constants in `gssapi.h`. Used by older applications that have not migrated to `GSS_C_NT_*`.

Risks: Deprecated aliases can obscure which OID should be emitted. Some declarations lack `GSS_DLLIMP`, so Windows import/export behavior may differ across symbols.

Test signals: Compile legacy users, verify each alias points to the expected OID, and run name import tests using both deprecated and RFC names.
